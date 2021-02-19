## Settings

python:7

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

from event import App
from event.server.redis import Server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = App(base_dir=BASE_DIR)
config = {
    'url': 'redis://redis/3',
}
server = Server(**config)
app.register_server('default', server)

@server.handler(channels=['example:test:redis'])
def handle_example_message(message):
    print('Received message: ', message)

app.run_forever()

# send message
server.publish_soon(channel='example-test-redis',
                    message={
                        'test_id': 'redis',
                        'message': 'good test'
                    })

```

#### kafka
```python
# Run server
import os

from event import App
from event.server.kafka import Server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = App(base_dir=BASE_DIR)
config = {
    'url': 'kafka:9092',
}
server = Server(**config)
app.register_server('default', server)

@server.handler(topics=['example-test-kafka'])
def handle_example_message(message):
    print('Received message: ', message, message.value)

app.run_forever()

# send message
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

from event import App
from event.server.rabbitmq import Server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = App(base_dir=BASE_DIR)
config = {
    'url': 'amqp://rabbitmq:5672',
    'exchange': 'test',
    'exchange_type': 'topic',
}
server = Server(**config)
app.register_server('default', server)

@server.handler(routing_key='example-test-rabbitmq',
                queue='example-test-rabbitmq-queue')
def handle_example_message(message):
    print('Received message: ', message)

app.run_forever()

# send message
server.publish_soon(routing_key='example-test-rabbitmq',
                    message={
                        'test_id': 'rabbitmq',
                        'message': 'good test'
                    })

```

### TODOLIST
