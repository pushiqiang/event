import os

from event import App
from event.server.rabbitmq import Server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = App(base_dir=BASE_DIR)
config = {
    'url': 'amqp://rabbitmq:5672',
    'exchange': 'test',
    'exchange_type': 'topic',
}
app.register_server('default', Server(**config))
