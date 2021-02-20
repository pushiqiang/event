# coding: utf-8
try:
    import ujson as json
except ImportError:
    import json
import asyncio
import logging

import aioamqp
import aioamqp.properties
import aioamqp.protocol

from .base import BaseConsumer, BaseServer, meth_comspec_name

logger = logging.getLogger(__name__)


class Consumer(BaseConsumer):
    def __init__(self,
                 server,
                 channel,
                 queue,
                 handler,
                 deserializer=None,
                 timeout=10):
        self.server = server
        self.channel = channel
        self.queue = queue
        self.handler = handler
        self.deserializer = deserializer
        self.timeout = timeout
        self._channel = None

    async def handle_message(self, message):
        if self.deserializer:
            message = self.deserializer(message)

        if asyncio.iscoroutinefunction(self.handler):
            fu = asyncio.ensure_future(self.handler(message),
                                       loop=self.server.loop)
        else:
            fu = self.server.loop.run_in_executor(None, self.handler, message)
        await asyncio.wait_for(fu, self.timeout, loop=self.server.loop)

    async def __on_message(self, channel, body, envelope, properties):
        encoding = properties.content_encoding or 'utf-8'
        message = body.decode(encoding)
        try:
            await self.handle_message(message)
        except Exception as ex:
            logger.error('Consume({}) message error.'.format(self.handler),
                         exc_info=ex)
        finally:
            await channel.basic_client_ack(envelope.delivery_tag)

    async def start(self):
        await self.channel.basic_consume(self.__on_message, self.queue)


class Server(BaseServer):
    def __init__(self, url, exchange, exchange_type, loop=None):
        self.url = url
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.loop = loop or asyncio.get_event_loop()
        self.consumers = set()
        self.status = 'INIT'  # INIT -> CONNECTED -> RUNNING | CLOSED
        self._connection = None
        self._channel = None

    @property
    def producer(self):
        return self._channel

    async def start(self):
        if self.status == 'RUNNING':
            raise Exception('Server({}) already started'.format(self.url))
        if not self._connection:
            self._connection = await self.create_rabbitmq_connection()
        self._channel = await self._connection.channel()
        self.status = 'CONNECTED'
        await self._channel.exchange_declare(self.exchange,
                                             self.exchange_type,
                                             durable=True)
        self.__start_consumers()
        print('Message processing server for rabbitmq is running...')

    async def __on_error(self, exc):
        self.status = 'CLOSED'
        self._connection = None
        self._channel = None
        logger.error('Connection({}) exception.'.format(self.url),
                     exc_info=exc)

    async def create_rabbitmq_connection(self, **kwargs):
        _, _connection = await aioamqp.from_url(self.url,
                                                login_method='PLAIN',
                                                on_error=self.__on_error,
                                                loop=self.loop,
                                                **kwargs)
        return _connection

    def __start_consumers(self):
        for c in self.consumers:
            self.loop.create_task(c.start())
        self.status = 'RUNNING'

    async def publish(self, routing_key, message, serializer=json.dumps):
        if serializer:
            try:
                message = serializer(message).encode()
            except Exception as e:
                logger.error('Serialize message error.', exc_info=True)
                raise e

        await self._channel.basic_publish(message, self.exchange, routing_key)

    def publish_soon(self, routing_key, message, serializer=json.dumps):
        asyncio.run_coroutine_threadsafe(
            self.publish(routing_key, message, serializer), self.loop)

    def publish_wait(self, routing_key, message, serializer=json.dumps):
        self.loop.run_until_complete(self.publish(routing_key, message, serializer))

    async def __subscribe_channel(self, routing_key, queue):
        _channel = await self._connection.channel()
        await _channel.queue_declare(queue, durable=True)
        await _channel.queue_bind(queue,
                                  self.exchange,
                                  routing_key=routing_key)
        return _channel

    async def subscribe(self,
                        routing_key,
                        queue,
                        handler,
                        deserializer=json.loads,
                        timeout=10,
                        **kwargs):
        if not self._connection:
            self._connection = await self.create_rabbitmq_connection(**kwargs)
        subscribed_channel = await self.__subscribe_channel(routing_key, queue)
        consumer = Consumer(server=self,
                            channel=subscribed_channel,
                            queue=queue,
                            handler=handler,
                            deserializer=deserializer,
                            timeout=timeout)
        self.consumers.add(consumer)
        if self.status == 'RUNNING':
            self.loop.create_task(consumer.start())

        print('Register handler[{}] -> queue[{}]'.format(meth_comspec_name(handler), queue))

    def handler(self,
                routing_key,
                queue=None,
                deserializer=json.loads,
                timeout=10,
                **kwargs):
        """
        添加事件处理器的装饰器
        :param routing_key: 路由键
        :param queue: 队列，若为None，则为消息处理函数的全路径名
        :param deserializer: 消息解析器 json.loads
        :param timeout: 处理的超时时长，默认值10秒，优先级 默认值 < 装饰器设置
        :return:
        """
        def decorator(func):
            asyncio.run_coroutine_threadsafe(self.subscribe(
                routing_key=routing_key,
                queue=queue or meth_comspec_name(func),
                handler=func,
                deserializer=deserializer,
                timeout=timeout,
                **kwargs),
                                             loop=self.loop)
            return func

        return decorator
