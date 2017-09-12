"""
JSON file flattener
"""

from .core import list_keys
from .core import get_items
from .tokenizer import SLICE_RE
from .inspector import inspect_json, count_arrays
from .treecrawler import find_keys

"""
TODO:
    1.  flatten only certain keys listed as a func argument
    2.  flatten using slice operator (i.e. only partial arrays, etc.)
    3.
"""


def flatten_all(d):
    """
    Flattens the entire json-serialized document in the jsoncut list format

    i.e. {'k1': 'item1', 'key2': {'key3': 'item3'}}

    Returns:
    {'k1': 'item1', 'key2.key3': 'item3'}
    """
    flattened = {}
    joined_keys = find_keys(d)
    for key in joined_keys:
        items = get_items(d, key.split('.'), fullpath=True)
        if not isinstance(items[key], dict):
            flattened[key] = items[key]
    return flattened



def flatten_by_keylist(d, keys=None):
    if keys == None:
        return flatten_all(d)
    pass



def main():
    flatten_all(EXAMPLE)
