"""
JSON File Flattener

Functions used to flatten a json-serialized document in the jsoncut list
format.

Functions:
    1.  flatten_all -> flatten the entire document
    2.  flatten_by_keys -> only flatten user-specified keys
    3.

TODO:
    1.  flatten using slice operator (i.e. only partial arrays, etc.)
    2.
"""

#from .core import list_keys
from .core import get_items
from .tokenizer import SLICE_RE                     # may not need
from .inspector import inspect_json, count_arrays   # may not need
from .treecrawler import find_keys
from . import exceptions as exc                     # may not need


def flatten_all(d):
    """
    Flattens the entire json-serialized document in the jsoncut list format

    PARAMS:
    d = json-serialized document converted to a python dict
        i.e. {'key1': 'item1', 'key2': {'key3': 'item3'}}

    RETURNS:
    {'key1': 'item1', 'key2.key3': 'item3'}
    """
    return flatten_by_keys(d)


def flatten_by_keys(d, keys=None):
    """
    Flattens the specified keys in the json-serialized document.
    If keys=None, or not specified, then the entire document is flattened.

    PARAMS:
    d = json-serialized document converted to a python dict
        i.e. {'key1': 'item1', 'key2': {'key3': 'item3'}}

    keys = singleton or list of jsoncut-style keys, such as:
        keys='key1'
        keys=['key1', 'key2.key3']

    RETURNS:
    flattened -> A dictionary with the flattened content
        i.e. {'key1': 'item1'}
             {'key2.key3': 'item3'}
    """
    flattened = {}
    jsoncut_keys = find_keys(d)
    if keys == None:
        keys = jsoncut_keys
    for key in keys:
        get_key_content(d, key, flattened)
    return flattened


def get_key_content(source, key, destination):
    """
    Utility function that returns the content of a jsoncut-style key.
    If the content is another dictionary, then the key is incomplete and does
    not set content in the destination dictionary.

    RAISES:
    jsoncut.exceptions.KeyNotFound via jsoncut.core.get_items() if invalid key
    """
    items = get_items(source, key.split('.'), fullpath=True)
    if not isinstance(items[key], dict):
        destination[key] = items[key]
