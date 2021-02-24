## Message processing framework (redis/kafka/rabbitmq) 

Requirement: python:3.7

### PEP8 Check
```
yapf -dr . | (! grep '.')
pylava .
isort -rc . --check-only --diff
```

### Usages

#### test
```
1. cd examples
2. setup docker container by `sudo docker-compose up -d`
3. enter container terminal_1 by `sudo docker exec -it your_container_id bash` and run main.py
4. enter a new container terminal_2 and run send_message.py 
```

#### in django
```python
# event_manager.py
import os
from event import Manager
from event.server.kafka import Server as KafkaServer
from event.server.rabbitmq import Server as RabbitmqServer
from event.server.redis import Server as RedisServer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
manager = Manager(base_dir=BASE_DIR)
manager.register_server('redis', RedisServer(url='redis://redis/3'))
manager.register_server('kafka', KafkaServer(url='kafka:9092'))

# wsgi.py
import os
from django.core.wsgi import get_wsgi_application
from .event_manager import manager

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")
application = get_wsgi_application()
manager.run_in_django()

# handlers.py
from example.event_manager import manager

redis_server = manager.get_server('redis')
kafka_server = manager.get_server('kafka')

@redis_server.handler(channels=['example:test:django'])
def handle_example_django_redis(message):
    print('Received redis message', message)


@kafka_server.handler(topics=['example-test-django'])
def handle_example_django_kafka(message):
    print('Received kafka message: ', message, message.value)

# views.py
from django.shortcuts import HttpResponse
from django.views import View
from example.event_manager import manager

redis_server = manager.get_server('redis')
kafka_server = manager.get_server('kafka')

class TestView(View):
    def get(self, request, *args, **kwargs):
        redis_server.publish_wait(channel='example:test:django',
                                  message={
                                      'test_id': 'redis_id',
                                      'message': 'redis good'
                                  })
        kafka_server.publish_wait(topic='example-test-django',
                                  message={
                                      'test_id': 'kafka_id',
                                      'message': 'kafka good'
                                  })
        return HttpResponse('good')
```


#### redis
```python
# Run server
import os

from event import Manager
from event.server.redis import Server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
manager = Manager(base_dir=BASE_DIR)
config = {
    'url': 'redis://redis/3',
}
server = Server(**config)
manager.register_server('default', server)

@server.handler(channels=['example:test:redis'])
def handle_example_message(message):
    print('Received message: ', message)

manager.run_forever()

# send message
await server.publish(channel='example-test-redis',
                     message={
                         'test_id': 'redis',
                         'message': 'good test'
                     })
# OR
server.publish_soon(channel='example-test-redis',
                    message={
                        'test_id': 'redis',
                        'message': 'good test'
                    })
# OR
server.publish_wait(channel='example-test-redis',
                    message={
                        'test_id': 'redis',
                        'message': 'good test'
                    })

```

#### kafka
```python
# Run server
import os

from event import Manager
from event.server.kafka import Server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
manager = Manager(base_dir=BASE_DIR)
config = {
    'url': 'kafka:9092',
}
server = Server(**config)
manager.register_server('default', server)

@server.handler(topics=['example-test-kafka'])
def handle_example_message(message):
    print('Received message: ', message, message.value)

manager.run_forever()

# send message
await server.publish(topic='example-test-kafka',
                     message={
                         'test_id': 'kafka',
                         'message': 'good test'
                     })
# OR
server.publish_soon(topic='example-test-kafka',
                    message={
                        'test_id': 'kafka',
                        'message': 'good test'
                    })

```


#### rabbitmq
```python
# Run server
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
server = Server(**config)
manager.register_server('default', server)

@server.handler(routing_key='example-test-rabbitmq',
                queue='example-test-rabbitmq-queue')
def handle_example_message(message):
    print('Received message: ', message)

manager.run_forever()

# send message
await server.publish(routing_key='example-test-rabbitmq',
                     message={
                         'test_id': 'rabbitmq',
                         'message': 'good test'
                     })
# OR
server.publish_soon(routing_key='example-test-rabbitmq',
                    message={
                        'test_id': 'rabbitmq',
                        'message': 'good test'
                    })

```

### TODO-LIST
- [ ] 消息异常处理
- [ ] 消息处理确认
- [ ] 消息处理重试
