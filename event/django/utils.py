import os


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
