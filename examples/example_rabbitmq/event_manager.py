import os

from event import Manager
from event.server.rabbitmq import Server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
manager = Manager(base_dir=BASE_DIR)
config = {
    'url': 'amqp://rabbitmq:5672',
    'exchange': 'test',
    'exchange_type': 'topic',
}
manager.register_server('default', Server(**config))
