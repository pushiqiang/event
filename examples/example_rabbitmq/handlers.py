from event_manager import manager

server = manager.get_server('default')


@server.handler(routing_key='example-test-sync')
def handle_example_sync(message):
    print('Received message: ', message)


@server.handler(routing_key='example-multi-test',
                queue='example-multi-test-queue')
@server.handler(routing_key='example-test-async',
                queue='example-test-sync-queue')
async def handle_example_async(message):
    print('Received async message: ', message)
