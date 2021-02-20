from event_manager import manager

server = manager.get_server('default')


@server.handler(topics=['example-test-sync'])
def handle_example_sync(message):
    print('Received message: ', message, message.value)


@server.handler(topics=['example-multi-async-test', 'example-multi-test'])
@server.handler(topics=['example-test-async'])
async def handle_example_async(message):
    print('Received async message: ', message, message.value)
