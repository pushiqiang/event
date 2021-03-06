import os

from event import Manager
from event.server.redis import Server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
manager = Manager(base_dir=BASE_DIR)
manager.register_server('default', Server(url='redis://redis/3'))
