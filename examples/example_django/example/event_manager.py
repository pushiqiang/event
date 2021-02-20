import os

from event import Manager
from event.server.kafka import Server as KafkaServer
from event.server.rabbitmq import Server as RabbitmqServer
from event.server.redis import Server as RedisServer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
manager = Manager(base_dir=BASE_DIR)
manager.register_server('redis', RedisServer(url='redis://redis/3'))
manager.register_server('kafka', KafkaServer(url='kafka:9092'))

config = {
    'url': 'amqp://rabbitmq:5672',
    'exchange': 'test',
    'exchange_type': 'topic',
}
manager.register_server('rabbitmq', RabbitmqServer(**config))
