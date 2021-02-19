try:
    import ujson as json
except ImportError:
    import json

import asyncio
import logging

import aiokafka

from .base import BaseConsumer, BaseServer

logger = logging.getLogger(__name__)


class Consumer(BaseConsumer):
    def __init__(self,
                 server,
                 topics,
                 handler,
                 group_id=None,
                 key_deserializer=None,
                 value_deserializer=None,
                 enable_auto_commit=True,
                 timeout=10,
                 **kwargs):
        self.server = server
        self.topics = topics
        self.group_id = group_id
        self.handler = handler
        self.timeout = timeout
        self.key_deserializer = key_deserializer
        self.value_deserializer = value_deserializer
        self.enable_auto_commit = enable_auto_commit
        self.kwargs = kwargs
        self._consumer = None

    async def handle_message(self, message):
        if asyncio.iscoroutinefunction(self.handler):
            fu = asyncio.ensure_future(self.handler(message),
                                       loop=self.server.loop)
        else:
            fu = self.server.loop.run_in_executor(None, self.handler, message)
        await asyncio.wait_for(fu, self.timeout, loop=self.server.loop)

    async def __on_message(self, consumer):
        async for msg in consumer:
            try:
                await self.handle_message(msg)
            except Exception as ex:
                logger.error('Consume(%s) message error.',
                             self.handler,
                             exc_info=ex)

    async def create_kafka_consumer(self):
        _consumer = aiokafka.AIOKafkaConsumer(
            loop=self.server.loop,
            group_id=self.group_id,
            bootstrap_servers=self.server.url,
            key_deserializer=self.key_deserializer,
            value_deserializer=self.value_deserializer,
            enable_auto_commit=self.enable_auto_commit,
            **self.kwargs)
        await _consumer.start()
        _consumer.subscribe(topics=self.topics)
        return _consumer

    async def start(self):
        self._consumer = await self.create_kafka_consumer()
        await self.__on_message(self._consumer)


class Server(BaseServer):
    """
    Kafka消息服务
    """
    def __init__(self, url, loop=None):
        self.url = url
        self.loop = loop or asyncio.get_event_loop()
        self.consumers = set()
        self._producer = None
        self.status = 'INIT'  # INIT -> CONNECTED -> RUNNING | CLOSED

    @property
    def producer(self):
        return self._producer

    async def create_kafka_producer(self):
        _producer = aiokafka.AIOKafkaProducer(loop=self.loop,
                                              bootstrap_servers=self.url)
        await _producer.start()
        return _producer

    async def publish(self, topic, message, serializer=json.dumps, **kwargs):
        if serializer:
            try:
                message = serializer(message).encode()
            except Exception as e:
                logger.error('Serialize message error.', exc_info=True)
                raise e

        await self._producer.send_and_wait(topic, message)

    def publish_soon(self, topic, message, serializer=json.dumps):
        """
        发送消息
        """
        asyncio.run_coroutine_threadsafe(
            self.publish(topic, message, serializer), self.loop)

    async def subscribe(self,
                        topics,
                        handler,
                        group_id,
                        key_deserializer=None,
                        value_deserializer=None,
                        enable_auto_commit=True,
                        timeout=10,
                        **kwargs):
        """
        订阅频道
        """
        consumer = Consumer(self, topics, handler, group_id, key_deserializer,
                            value_deserializer, enable_auto_commit, timeout,
                            **kwargs)
        self.consumers.add(consumer)
        if self.status == 'RUNNING':
            self.loop.create_task(consumer.start())

    def __start_consumers(self):
        for c in self.consumers:
            self.loop.create_task(c.start())
        self.status = 'RUNNING'

    async def start(self):
        if self.status == 'RUNNING':
            raise Exception('Server({}) already started'.format(self.url))

        self._producer = await self.create_kafka_producer()
        self.status = 'CONNECTED'
        self.__start_consumers()

    def handler(self,
                topics,
                group_id=None,
                key_deserializer=None,
                value_deserializer=lambda x: json.loads(x.decode()),
                enable_auto_commit=True,
                timeout=10,
                **kwargs):
        """
        添加事件处理器的装饰器
        :param topics: 订阅的topics
        :param group_id: group_id
        :param key_deserializer: key deserializer
        :param value_deserializer: value deserializer
        :param enable_auto_commit: 是否自动提交，默认True
        :param timeout: 处理的超时时长，默认值10秒，优先级 默认值 < settings设置 < 装饰器设置
        :return:
        """
        def decorator(func):
            asyncio.run_coroutine_threadsafe(self.subscribe(
                topics=topics,
                handler=func,
                group_id=group_id,
                key_deserializer=key_deserializer,
                value_deserializer=value_deserializer,
                enable_auto_commit=enable_auto_commit,
                timeout=timeout,
                **kwargs),
                                             loop=self.loop)
            return func

        return decorator
