"""
WSGI config for example project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# 启动时创建mq消息服务
from .event_manager import manager

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

application = get_wsgi_application()

manager.run_in_django()
