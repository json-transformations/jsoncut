"""Sequence items for functs that accept a sequence or single element.

Without this module typical behavior is as follows:

    1. foo(['item1', 'item2', ...]) processes 'item1', 'item2', etc.
    2. foo('item') process 'i', 't', 'e', 'm'

This module is a simple wrapper for cases when the desired behavior in
example 2 above is to process 'item1' as a string and not
['i', 't', 'e', 'm'],

Examples:
    >>> sequence = Items('item1')
    >>> sequence.items = [i.upper() for i in sequence.items]
    >>> sequence.value
    'ITEM1'

    >>> sequence = Items(['item1', 'item2'])
    >>> sequence.items = [i.upper() for i in sequence.items]
    >>> sequence.value
    ['ITEM1', 'ITEM2']
"""
from collections import Sequence
from copy import deepcopy


def is_sequence_and_not_str(obj):
    """Exclude strings when determining whether an object is a Sequence.

    Examples:
        >>> types = [[], tuple(), set(), {}, '', 5, True, None]
        >>> [is_sequence_and_not_str(i) for i in types]
        [True, True, False, False, False, False, False, False]
    """
    return isinstance(obj, Sequence) and not isinstance(obj, str)


class Items(object):
    """Wrap a string or non-sequence in a list."""

    def __init__(self, obj):
        """Wrap a string or non-Sequence in a list."""
        self.items = deepcopy(obj)
        self.is_str_or_not_sequence = not is_sequence_and_not_str(obj)
        if self.is_str_or_not_sequence:
            self.items = [self.items]

    @property
    def value(self):
        """Unwrap if applicable; return the original object type."""
        if self.is_str_or_not_sequence:
            return self.items[0]
        return self.items
