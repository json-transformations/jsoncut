import logging

from boltons.iterutils import _UNSET, PathAccessError, get_path

from .errors import PathAssignmentError

logger = logging.getLogger('jsoncut')
logger.addHandler(logging.NullHandler())


def get_value(path, data, default=None):
    try:
        return get_path(data, path)
    except PathAccessError as e:
        logger.debug('get_value ' + str(e))
        if default == _UNSET:
            raise
        return default


def get_parent(path, data, **kwargs):
    if len(path) == 1:
        return data
    return get_value(path[:-1], data, **kwargs)


def set_value(path, value, data, suppress=True):
    try:
        parent = get_parent(path, data, default=_UNSET)
    except PathAccessError as e:
        logger.debug('set_value ' + str(e))
        if not suppress:
            raise
        return data
    try:
        parent[path[-1]] = value
    except (IndexError, TypeError) as e:
        logger.debug('set_value ' + str(e))
        if not suppress:
            raise PathAssignmentError(e, path[-1], path, value)
    return data


def get_item(path, data, fullpath=False, **kwargs):
    into_key = '.'.join(path) if fullpath else path[-1]
    return into_key, get_value(path, data, **kwargs)


def del_item(path, data, **kwargs):
    del get_parent(path, data, **kwargs)[path[-1]]


def get_values(data):
    pass


def get_paths(data):
    pass
