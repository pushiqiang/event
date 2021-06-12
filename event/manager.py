import asyncio
import threading
from .context import set_global_manager
from .utils import auto_load_handlers


class SingleMeta(type):
    """
    Thread-safe singleton metaclass
    """
    __instance = None
    __lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not SingleMeta.__instance:
            with SingleMeta.__lock:
                if not SingleMeta.__instance:
                    SingleMeta.__instance = object.__new__(cls)
                    cls.__init__(SingleMeta.__instance, *args, **kwargs)
        return SingleMeta.__instance


class Manager(metaclass=SingleMeta):
    def __init__(self, base_dir, auto_load_handler=True, loop=None):
        self._server_repo = {}
        self.base_dir = base_dir
        self.auto_load_handler = auto_load_handler
        self.loop = loop or asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        set_global_manager(self)

    def _auto_load_handler(self):
        if self.auto_load_handler:
            auto_load_handlers(self.base_dir)

    def register_server(self, name, server):
        self._server_repo[name] = server

    def get_server(self, name):
        return self._server_repo.get(name)

    async def run(self):
        for server in self._server_repo.values():
            await server.start()
        self._auto_load_handler()

    def run_forever(self):
        for server in self._server_repo.values():
            self.loop.run_until_complete(server.start())
        self._auto_load_handler()
        self.loop.run_forever()

    def _run_in_thread(self):
        for server in self._server_repo.values():
            asyncio.run_coroutine_threadsafe(server.start(), self.loop)

        t = threading.Thread(target=self.loop.run_forever)
        t.setDaemon(True)
        t.start()

    def run_in_thread(self):
        self._run_in_thread()
        self._auto_load_handler()

    def run_in_django(self):
        from event.django.utils import django_auto_load_handlers
        self._run_in_thread()
        if self.auto_load_handler:
            django_auto_load_handlers()
