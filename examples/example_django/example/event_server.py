import os

from event import App
from event.server.kafka import Server as KafkaServer
from event.server.rabbitmq import Server as RabbitmqServer
from event.server.redis import Server as RedisServer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = App(base_dir=BASE_DIR)
app.register_server('redis', RedisServer(url='redis://redis/3'))
app.register_server('kafka', KafkaServer(url='kafka:9092'))

config = {
    'url': 'amqp://rabbitmq:5672',
    'exchange': 'test',
    'exchange_type': 'topic',
}
app.register_server('rabbitmq', RabbitmqServer(**config))
