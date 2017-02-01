# import json
from collections import Mapping, deque, namedtuple

from .sequencer import is_sequence_and_not_str
from .treecrawler import Node

import click

MinMax = {i: namedtuple(i, ['min', 'max'])
          for i in ('Count', 'Keys', 'Len', 'Val')}


def set_min_max(type_, key, val, types):
    mm = MinMax[key]
    if type_ not in types:
        types[type_] = mm(val, val)
    else:
        types[type_] = mm(min(types[type_][0], val), max(types[type_][1], val))
    return types


def get_json_type(obj, types):
    if obj is None:
        types['null'] = True
    elif obj is True:
        types['true'] = True
    elif obj is False:
        types['false'] = True
    elif isinstance(obj, Mapping):
        return set_min_max('Object', 'Keys', len(obj.keys()), types)
    elif is_sequence_and_not_str(obj):
        return set_min_max('Array', 'Count', len(obj), types)
    elif isinstance(obj, str):
        return set_min_max('Text', 'Len', len(obj), types)
    elif isinstance(obj, (float, int)):
        return set_min_max('Number', 'Val', obj, types)
    return types


def fmt_type(type_):
    key, value = type_
    if key in ('true', 'false', 'null'):
        return key

    key, name = key.lower(), value.__class__.__name__.lower()
    if value.min == value.max:
        return '{0}({1}={2})'.format(key, name, value.min)
    return '{0}(min{1}={2[0]}, max{1}={2[1]})'.format(key, name, value)


def format_result(keys, nocolor=False, keys_fg='white', types_fg='cyan'):
    d = dict(keys)
    fmt_types = [[fmt_type(j) for j in i.items()] for i in d.values()]
    fmt_types = [' | '.join(i) if len(i) > 1 else i[0] for i in fmt_types]
    padding = len(max(d.keys(), key=len))
    fmt_keys = [i.ljust(padding) for i in d.keys()]
    if not nocolor:
        fmt_keys = [click.style(i, fg=keys_fg) for i in fmt_keys]
        fmt_types = [click.style(i, fg=types_fg) for i in fmt_types]
    for key, val in zip(fmt_keys, fmt_types):
        yield key + ' :' + val


def get_children(parent, visited, types):
    """Return a list of child nodes."""
    path, obj = parent
    if isinstance(obj, Mapping):
        children = obj.items()
    elif is_sequence_and_not_str(obj):
        children = [('#', i) for i in obj]
    else:
        return []
    return [Node('{}.{}'.format(path, k), v) for k, v in children]


def key_crawler(d, nodes=None):
    visited, types = set(), dict()
    to_crawl = deque([Node('', d)] if nodes is None else nodes)
    while to_crawl:
        node = to_crawl.popleft()
        visited.add(node.path)
        types[node.path] = get_json_type(node.obj, types.get(node.path, {}))
        to_crawl.extend(get_children(node, visited, types))
    return {i: types[i] for i in visited if i}


def tree_walker(d):
    """Return a sorted list of keys from a JSON document."""
    seq = is_sequence_and_not_str(d)
    nodes = None if not seq else get_children(('', d), set(), {})
    return sorted((k.lstrip('.'), v) for k, v in key_crawler(d, nodes).items())


def inspect_json(d):
    return format_result(tree_walker(d))
