import os

from event import App
from event.server.kafka import Server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = App(base_dir=BASE_DIR)
app.register_server('default', Server(url='kafka:9092'))
