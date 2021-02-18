import asyncio
import importlib
import os
import threading


def auto_load_handlers(path):
    """
    自动加载handlers.py脚本
    """
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if item.endswith('handlers.py'):
            importlib.import_module(item[:-3], item_path)
        elif os.path.isdir(item_path):
            auto_load_handlers(item_path)


def django_auto_load_handlers():
    """
    django启动时自动加载handlers.py脚本，主要用于需要启动时加载的功能，例如: 事件处理函数
    """
    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        app_path = app.replace('.', '/')
        if not os.path.isdir(app_path):
            continue
        for item in os.listdir(app_path):
            if item.endswith('handlers.py'):
                __import__('{pkg}.{mdl}'.format(pkg=app, mdl=item[:-3]))


class App:
    def __init__(self, base_dir, auto_load_handler=True, loop=None):
        self._server_repo = {}
        self.base_dir = base_dir
        self.auto_load_handler = auto_load_handler
        self.loop = loop or asyncio.get_event_loop()

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
        asyncio.set_event_loop(self.loop)
        for server in self._server_repo.values():
            asyncio.run_coroutine_threadsafe(server.start(), self.loop)

        t = threading.Thread(target=self.loop.run_forever)
        # t.setDaemon(True)
        t.start()

    def run_in_thread(self):
        self._run_in_thread()
        self._auto_load_handler()

    def run_in_django(self):
        self._run_in_thread()
        if self.auto_load_handler:
            django_auto_load_handlers()
