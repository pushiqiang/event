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
