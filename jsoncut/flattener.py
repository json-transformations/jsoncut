"""
JSON file flattener
"""

from .core import list_keys
from .tokenizer import SLICE_RE
from .inspector import inspect_json, count_arrays



def flatten_all(d):
    keys = [item.split(' ')[-1] for item in list_keys(d)]
    pass


def flatten_by_keylist(d, keys=None):
    if keys == None:
        return flatten_all(d)
    pass
