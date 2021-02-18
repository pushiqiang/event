import abc


class BaseConsumer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def handle_message(self, message):
        pass

    @abc.abstractmethod
    async def start(self):
        pass

    async def ack(self):
        pass

    async def retry_deliver(self, message):
        pass


class BaseServer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def start(self):
        pass

    @abc.abstractmethod
    async def publish(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def publish_soon(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def subscribe(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def handler(self, *args, **kwargs):
        pass
