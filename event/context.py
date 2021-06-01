# coding: utf-8

manager = None


def global_manager():
    """Returns the global manager.
    The default value is an instance of :class:`event.manager.Manager`

    :rtype: :class:`Manager`
    :return: The global manager instance.
    """
    return manager


def set_global_manager(value):
    """Sets the global manager.
    It is an error to pass ``None``.

    :param value: the :class:`Manager` used as global instance.
    :type value: :class:`Manager`
    """
    if value is None:
        raise ValueError('The global Manager cannot be None')

    global manager
    manager = value
