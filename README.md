## Message processing framework (redis/kafka/rabbitmq) 

Requirement: python:7

### PEP8 Check
```
yapf -dr . | (! grep '.')
pylava .
isort -rc . --check-only --diff
```

### Usages

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