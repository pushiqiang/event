from event_manager import manager

if __name__ == '__main__':
    server = manager.get_server('default')

    manager.loop.run_until_complete(manager.run())
    manager.loop.run_until_complete(
        server.publish(routing_key='example-test-sync',
                       message={
                           'test_id': 'xxxxxxxxxxx',
                           'message': 'good test'
                       }))
    manager.loop.run_until_complete(
        server.publish(routing_key='example-test-async',
                       message={
                           'test_id': 'nnnnnnnnnnn',
                           'message': 'good test'
                       }))
    manager.loop.run_until_complete(
        server.publish(routing_key='example-test-async',
                       message={
                           'test_id': '好好学习',
                           'message': 'good test'
                       }))
    manager.loop.run_until_complete(
        server.publish(routing_key='example-multi-test',
                       message={
                           'name': 'patrick',
                           'message': 'patrick你好'
                       }))
