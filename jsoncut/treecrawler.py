"""JSON Tree Crawler.

:param revisit:
    If True then perform a full-scan of the document crawling
    through every instance of the same key/path name looking for new
    objects & keys. If False and the key/path name has already been
    visited then don't bother crawling through it.

:param indexes:
    If True then scans each array index for new objects/keys.

.. note::
    Different nodes can have the same key-path name since sequence
    index numbers are all replaced with a '#' which serves as a
    wildcard character for unique key-path name representation.
    This function searches for unique key-paths not unique index
    numbers.
"""
import re
from collections import Mapping, deque, namedtuple

from .sequencer import is_sequence_and_not_str

Node = namedtuple('Node', ['path', 'obj'])
KEY_HEADER = re.compile(r'^(\.#\.|\.#|\.)')


def get_children(parent, visited, revisit, is_array=False):
    """Return a list of child nodes."""
    path, obj = parent
    if isinstance(obj, Mapping):
        children = obj.items()
    elif is_array:
        children = [('#', i) for i in obj]
    else:
        return []
    children = [Node('{}.{}'.format(path, k), v) for k, v in children]
    if revisit:
        return children
    return [i for i in children if i.path not in visited]


def key_crawler(d, nodes=None, revisit=True):
    """Return sorted set of unique key-paths from a Mapping."""
    visited = set()
    to_crawl = deque([Node('', d)] if nodes is None else nodes)
    while to_crawl:
        current = to_crawl.popleft()
        if revisit or current.path not in visited:
            if current.path and current.path not in visited:
                visited.add(current.path)
            to_crawl.extend(get_children(current, visited, revisit))
    return visited


def find_keys(d, fullscan=False):
    """Return a sorted list of keys from a JSON document."""
    seq = is_sequence_and_not_str(d)
    nodes = get_children(('', d), set(), True, True) if seq else None
    result = (KEY_HEADER.sub('', i) for i in key_crawler(d, nodes, fullscan))
    return sorted(i for i in result if i)
