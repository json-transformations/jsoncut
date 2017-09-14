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
    :param d: = json-serialized document converted to a python dict
    :return: a flat dict with each key being in the jsoncut style

    Example:
    d = {'key1': 'item1', 'key2': {'key3': 'item3'}}
    returns: {'key1': 'item1', 'key2.key3': 'item3'}
    """
    return flatten_by_keys(d)


def flatten_by_keys(d, keys=None):
    """
    Flattens the specified keys in the json-serialized document.
    :param d: json-serialized document converted to a python dict
    :param keys: singleton or list of jsoncut-style keys.  If not specified, or
                 set to None, the entire document is flattened.
    :return: a dictionary with the flattened content

    Example:
    d = {'key1': 'item1', 'key2': {'key3': 'item3'}}
    keys = ['key2.key3']
    returns: {'key2.key3': 'item3'}
    """
    flattened = {}
    if keys == None:
        keys = find_keys(d)
    for key in keys:
        get_key_content(d, key, flattened)
    return flattened


def get_key_content(source, key, destination):
    """
    Utility function that returns the content of a jsoncut-style key.
    If the content is another dictionary, then the key is incomplete and does
    not set content in the destination dictionary.
    :param source: source dict created from json document
    :param key: a jsoncut style key
    :param destination: dict used by calling-function to load result into
    :raises: jsoncut.exceptions.KeyNotFound via jsoncut.core.get_items()
             if invalid key

    Example:
    source = {'key1': 'item1', 'key2': {'key3': 'item3'}}
    key = 'key2.key3'
    results in destination['key2.key3'] = 'item3'
    """
    items = get_items(source, key.split('.'), fullpath=True)
    if not isinstance(items[key], dict):
        destination[key] = items[key]
