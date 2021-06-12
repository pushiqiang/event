# coding: utf-8
import json
import logging
import threading

from event.context import global_manager

try:
    # needed to support Django >= 1.10 MIDDLEWARE
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # needed to keep Django <= 1.9 MIDDLEWARE_CLASSES
    MiddlewareMixin = object

logger = logging.getLogger(__name__)


class MessagePublishTransactionMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        """
        成功返回response后发送请求中产生的消息，确保事务性
        """
        if int(response.status_code / 100) in [2, 3]:
            code = 0
            try:
                code = json.loads(response.content.decode()).get('code', 0)
            except Exception:
                pass
            if code == 0:
                publish_after_response()
        return response


def publish_after_response():
    thread = threading.current_thread()
    message_queue = getattr(thread, 'message_queue', None) or []
    # 重置message_queue，谨防被另外使用
    setattr(thread, 'message_queue', [])
    try:
        manager = global_manager()
        for (server_name, args, kwargs) in message_queue:
            server = manager.get_server(server_name)
            server.publish_soon(*args, **kwargs)
    except Exception as e:
        logger.warning('Send message error after response', exc_info=e)
