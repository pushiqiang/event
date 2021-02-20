import importlib
import os


def auto_load_handlers(path):
    """
    自动加载handlers.py脚本
    """
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if item.endswith('handlers.py'):
            importlib.import_module(item[:-3], item_path)
        elif os.path.isdir(item_path):
            auto_load_handlers(item_path)


def django_auto_load_handlers():
    """
    django启动时自动加载所有INSTALLED_APPS模块的handlers.py脚本
    """
    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        app_path = app.replace('.', '/')
        if not os.path.isdir(app_path):
            continue
        for item in os.listdir(app_path):
            if item.endswith('handlers.py'):
                __import__('{pkg}.{mdl}'.format(pkg=app, mdl=item[:-3]))
