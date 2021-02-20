from event_manager import manager

server = manager.get_server('default')


@server.handler(channels=['example:test:sync'])
def handle_example_sync(message):
    print('Received message: ', message)


@server.handler(channels=['example:test:async'])
async def handle_example_async(message):
    print('Received async message: ', message)
