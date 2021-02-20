from event_manager import manager

if __name__ == '__main__':
    server = manager.get_server('default')

    manager.loop.run_until_complete(manager.run())
    manager.loop.run_until_complete(
        server.publish(topic='example-test-sync',
                       message={
                           'test_id': 'xxxxxxxxxxx',
                           'message': 'good test'
                       }))
    manager.loop.run_until_complete(
        server.publish(topic='example-test-async',
                       message={
                           'test_id': 'nnnnnnnnnnn',
                           'message': 'good test'
                       }))
    manager.loop.run_until_complete(
        server.publish(topic='example-multi-async-test',
                       message={
                           'name': 'patrick example-multi-async-test',
                           'message': '你好'
                       }))
    manager.loop.run_until_complete(
        server.publish(topic='example-multi-test',
                       message={
                           'name': 'patrick example-multi-test',
                           'message': '你好'
                       }))
