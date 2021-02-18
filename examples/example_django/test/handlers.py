from example.event_server import app

redis_server = app.get_server('redis')
kafka_server = app.get_server('kafka')
rabbitmq_server = app.get_server('rabbitmq')


@redis_server.handler(channels=['example:test:django'])
def handle_example_django_redis(message):
    print('Received redis message', message)


@kafka_server.handler(topics=['example-test-django'])
def handle_example_django_kafka(message):
    print('Received kafka message: ', message, message.value)


@rabbitmq_server.handler(routing_key='example:test:django',
                         queue='example:test:django')
def handle_example_django_rabbitmq(message):
    print('Received rabbitmq message: ', message)
