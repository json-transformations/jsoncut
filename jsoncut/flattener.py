"""
JSON File Flattener

Functions used to flatten a json-serialized document in the jsoncut list
format.

Functions:
    1.  flatten_all -> flatten the entire document
    2.  flatten_by_keys -> only flatten user-specified keys
    3.  generate_rows -> create rows of data from the json document for use
        as a dataframe or for other data analysis uses

TODO:
    1.  flatten using slice operator (i.e. only partial arrays, etc.)
"""

from .core import get_items
from .tokenizer import SLICE_RE                     # may not need
from .treecrawler import find_keys
from . import exceptions as exc



def flatten_all(d):
    """
    Flattens the entire json-serialized document in the jsoncut list format.

    :param d: = json-serialized document converted to a python dict.
    :return: a flat dict with each key being in the jsoncut style.

    Example:
    d = {'key1': 'item1', 'key2': {'key3': 'item3'}}
    returns: {'key1': 'item1', 'key2.key3': 'item3'}
    """
    return flatten_by_keys(d)


def flatten_by_keys(d, keys=None):
    """
    Flattens the specified keys in the json-serialized document.  If key has
    an array as the value with more key-value pairs, then each index in the
    array is flattened, as well.  If the key is a root key with a dict as a
    value, then recursively flattens that branch.

    :param d: json-serialized document converted to a python dict.
    :param keys: singleton or list of jsoncut-style keys.  If not specified, or
        set to None, the entire document is flattened.
    :return: a dictionary with the flattened content.

    Example:
    d = {'key1': 'item1', 'key2': {'key3': 'item3'}}
    keys = ['key2.key3']
    returns: {'key2.key3': 'item3'}
    """
    flattened = {}
    if keys == None:
        keys = find_keys(d)
    for key in keys:
        content = get_key_content(d, key)

        # flatten each item in an array, as well.
        if isinstance(content, list) and isinstance(content[0], dict):
            flattened[key] = []
            array_content = get_items(d, [key], fullpath=True)

            for item in array_content[key]:
                array_keys = find_keys(item)
                flattened[key].append(flatten_by_keys(item, array_keys))

        elif not isinstance(content, dict):
            flattened[key] = content

        elif isinstance(content, dict):
            flattened.update({'.'.join([key, k]):v for k,v in
                flatten_by_keys(content).items()})

    return flattened


def generate_rows(d, root_key, prepend_keys=None):
    """
    Generator function that generates rows of data from multiple entries in
    the root_key, with the option to prepend columns.  Useful when waning to
    create dataframes, or rows to export to a CSV file for data analysis.

    :param d: json-serialized document converted to a python dict.
    :param root_key: jsoncut-style key that specifies the root where all data
        is to be collected for the rows.
    :param prepend_keys: optional list of jsoncut-style keys that will prepend
        the data rows, such as data that is not part of the root_key data.
    :return: generates a dict for each row

    Example:
    d = {'key1': 'item1', 'key2': [{'date':'today'}, {'date': 'tomorrow'}]}
    root_key = 'key2'
    prepend_keys = ['key1']
    yield:
        {'key1':'item1', 'date': 'today'}
        {'key1':'item1', 'date': 'tomorrow'}
    """
    # add prepended data if requested
    prepend_data = {}
    if prepend_keys is not None:
        prepend_data.update(flatten_by_keys(d, prepend_keys))

    # get the content and create individual rows
    content_array = get_items(d, [root_key], fullpath=True)
    for item in content_array[root_key]:
        row = {}
        row.update(prepend_data)
        keys = find_keys(item)
        row.update(flatten_by_keys(item, keys))

        yield row


def get_key_content(source, key):
    """
    Utility function that returns the content of a jsoncut-style key.

    :param source: json-serialized document converted to a python dict.
    :param key: a jsoncut style key.
    :return: the value stored in the given key
    :raises: jsoncut.exceptions.KeyNotFound via jsoncut.core.get_items()
        if invalid key.

    Example:
    source = {'key1': 'item1', 'key2': {'key3': 'item3'}}
    key = 'key2.key3'
    returns 'item3'
    """
    items = get_items(source, key.split('.'), fullpath=True)
    return items[key]
