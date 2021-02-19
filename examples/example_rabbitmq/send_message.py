from event_server import app

if __name__ == '__main__':
    server = app.get_server('default')

    app.loop.run_until_complete(app.run())
    app.loop.run_until_complete(
        server.publish(routing_key='example-test-sync',
                       message={
                           'test_id': 'xxxxxxxxxxx',
                           'message': 'good test'
                       }))
    app.loop.run_until_complete(
        server.publish(routing_key='example-test-async',
                       message={
                           'test_id': 'nnnnnnnnnnn',
                           'message': 'good test'
                       }))
    app.loop.run_until_complete(
        server.publish(routing_key='example-test-async',
                       message={
                           'test_id': '好好学习',
                           'message': 'good test'
                       }))
    app.loop.run_until_complete(
        server.publish(routing_key='example-multi-test',
                       message={
                           'name': 'patrick',
                           'message': 'patrick你好'
                       }))
