from event_server import app

if __name__ == '__main__':
    server = app.get_server('default')

    app.loop.run_until_complete(app.run())
    app.loop.run_until_complete(
        server.publish(topic='example-test-sync',
                       message={
                           'test_id': 'xxxxxxxxxxx',
                           'message': 'good test'
                       }))
    app.loop.run_until_complete(
        server.publish(topic='example-test-async',
                       message={
                           'test_id': 'nnnnnnnnnnn',
                           'message': 'good test'
                       }))
    app.loop.run_until_complete(
        server.publish(topic='example-multi-async-test',
                       message={
                           'name': 'patrick example-multi-async-test',
                           'message': '你好'
                       }))
    app.loop.run_until_complete(
        server.publish(topic='example-multi-test',
                       message={
                           'name': 'patrick example-multi-test',
                           'message': '你好'
                       }))
