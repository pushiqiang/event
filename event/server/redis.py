try:
    import ujson as json
except ImportError:
    import json

import asyncio
import logging

import aioredis

from .base import BaseConsumer, BaseServer, meth_comspec_name

logger = logging.getLogger(__name__)


class Consumer(BaseConsumer):
    def __init__(self,
                 server,
                 channels,
                 handler,
                 deserializer=None,
                 timeout=10):
        self.server = server
        self.channels = channels
        self.handler = handler
        self.timeout = timeout
        self.deserializer = deserializer

    async def handle_message(self, message):
        if asyncio.iscoroutinefunction(self.handler):
            fu = asyncio.ensure_future(self.handler(message),
                                       loop=self.server.loop)
        else:
            fu = self.server.loop.run_in_executor(None, self.handler, message)
        await asyncio.wait_for(fu, self.timeout, loop=self.server.loop)

    async def __on_message(self, channel):
        async for message in channel.iter(encoding='utf-8',
                                          decoder=self.deserializer):
            try:
                await self.handle_message(message)
            except Exception as ex:
                logger.error('Consume({}) message error.'.format(self.handler),
                             exc_info=ex)

    async def start(self):
        _task = [self.__on_message(ch) for ch in self.channels]
        await asyncio.gather(*_task)


class Server(BaseServer):
    """
    Redis消息服务
    """
    def __init__(self, url, loop=None, heartbeat_interval=30):
        self.url = url
        self.loop = loop or asyncio.get_event_loop()
        self.consumers = set()
        self.status = 'INIT'  # INIT -> CONNECTED -> RUNNING | CLOSED
        self._is_keep_alive = False
        self._producer = None
        self._subs = list()
        self.heartbeat_interval = heartbeat_interval

    @property
    def producer(self):
        return self._producer

    async def publish(self, channel, message, serializer=json.dumps):
        if serializer:
            try:
                message = serializer(message).encode()
            except Exception as e:
                logger.error('Serialize message error.', exc_info=True)
                raise e

        await self._producer.publish(channel, message)

    def publish_soon(self, channel, message, serializer=json.dumps):
        asyncio.run_coroutine_threadsafe(
            self.publish(channel, message, serializer), self.loop)

    def publish_wait(self, channel, message, serializer=json.dumps):
        self.loop.run_until_complete(self.publish(channel, message, serializer))

    async def __subscribe_channels(self, sub, channels):
        _pattern_channel = []
        _channel = []

        for ch in channels:
            if '*' in ch:
                _pattern_channel.append(aioredis.Channel(ch, is_pattern=True))
            else:
                _channel.append(aioredis.Channel(ch, is_pattern=False))

        _subscribed_channels = []
        if _channel:
            _subscribed_channels = await sub.subscribe(*_channel)
        if _pattern_channel:
            _subscribed_channels.extend(await
                                        sub.psubscribe(*_pattern_channel))

        return _subscribed_channels

    async def create_redis_connection(self, **kwargs):
        connection = await aioredis.create_redis(self.url,
                                                 loop=self.loop,
                                                 **kwargs)
        return connection

    async def subscribe(self,
                        channels,
                        handler,
                        deserializer=json.loads,
                        timeout=10,
                        **kwargs):
        """
        订阅频道
        """
        sub = await self.create_redis_connection(**kwargs)
        self._subs.append(sub)
        await self.__keep_alive()

        _subscribed_channels = await self.__subscribe_channels(sub, channels)
        consumer = Consumer(self, _subscribed_channels, handler, deserializer,
                            timeout)
        self.consumers.add(consumer)
        if self.status == 'RUNNING':
            self.loop.create_task(consumer.start())
        print('Register handler[{}] -> channels[{}]'.format(meth_comspec_name(handler), ','.join(channels)))

    async def __keep_alive(self):
        if not self._is_keep_alive:
            # 有订阅维持心跳
            self.loop.create_task(self.__ping())
            self._is_keep_alive = True

    async def __ping(self):
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            # 向redis-server发送PING消息
            for i in range(len(self._subs)):
                if not (await self._subs[i].ping()):
                    self._subs[i] = await self.create_redis_connection()

    async def start(self):
        if self.status == 'RUNNING':
            raise Exception('Server({}) already started'.format(self.url))

        self._producer = await self.create_redis_connection()
        self.status = 'CONNECTED'
        self.__start_consumers()
        print('Message processing server is running...')

    def __start_consumers(self):
        for c in self.consumers:
            self.loop.create_task(c.start())
        self.status = 'RUNNING'

    def handler(self, channels, deserializer=json.loads, timeout=10, **kwargs):
        """
        添加事件处理器的装饰器
        :param channels: 订阅的频道 列表
        :param deserializer: 消息解析器 json.loads
        :param timeout: 处理的超时时长，默认值10秒，优先级 默认值 < 装饰器设置
        :return:
        """
        def decorator(func):
            asyncio.run_coroutine_threadsafe(self.subscribe(
                channels=channels,
                handler=func,
                deserializer=deserializer,
                timeout=timeout,
                **kwargs),
                                             loop=self.loop)
            return func

        return decorator
