# coding: utf-8
import threading


def publish(server_name='default', *args, **kwargs):
    """
    事务性发送：发送消息，并不立即发送，而是放到当前线程中，后续由MessagePublishTransactionMiddleware来负责真实发送
    django.settings添加中间件:
    MIDDLEWARE = (
        ...
        "event.django.middleware.MessagePublishTransactionMiddleware",
        ...
    )
    """
    message_queue = getattr(threading.current_thread(), 'message_queue', None) or []
    message_queue.append((server_name, args, kwargs))
    setattr(threading.current_thread(), 'message_queue', message_queue)
