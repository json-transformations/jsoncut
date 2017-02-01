"""JSON Cut Custom Exceptions."""
from collections import namedtuple

import click

from . import core

Color = namedtuple('Color', ['val', 'style'])


def color_error_mesg(fmtstr, kwds, nocolor=False):
    """asterix before color name indicates bold."""
    if nocolor:
        kwds = {k: v.val for k, v in kwds.items()}
    else:
        def get_style(c):
            return dict(fg=c.style.lstrip('*'), bold=c.style.startswith('*'))
        kwds = {k: click.style(str(v.val), **get_style(v))
                for k, v in kwds.items()}
    return fmtstr.format(**kwds)


def default_error_mesg_fmt(exc, colorless=False):
    return color_error_mesg('{err_name}: {err_mesg}', {
        'err_name': Color(exc.__class__.__name__, '*red'),
        'err_mesg': Color(str(exc), 'white')
    }, colorless)


class JsonCutError(Exception):
    """JSON Cut Base Exception."""

    def format_error(self, nocolor=False):
        return default_error_mesg_fmt(self, nocolor)


class KeyNumberOutOfRange(JsonCutError, ValueError):
    """Invalid Key-Number."""
    pass


class KeyTypeError(JsonCutError, TypeError):
    """The key or index was not found in the JSON document."""
    def __init__(self, exc, op=None, key=None, itemnum=0, data=None,
                 keylist=None):
        """Initialize KeyNotFound Exception.

        Kwds:
            fn (str): name of module/funct where exception was raised
            item (self):  JSON data from which the key was missing
        :param keylist: a list of available keys
        """
        msg = str(exc)
        super(KeyTypeError, self).__init__(msg)
        self.operation = op
        self.item_number = itemnum
        self.data = data
        self.keylist = keylist

    def format_error(self, nocolor=False):
        mesg = (
            '{dashed_line}\n'
            '{error}\n'
            '{dashed_line}\n'
            'Operation: {operation}\n'
            'Item #: {item_number}\n'
            'Parsed Key List: {key_list}\n'
        )
        kwds = {
            'error': Color(self.args[0], '*red'),
            'dashed_line': Color('-' * 40, 'yellow'),
            'item_number': Color(self.item_number, 'red'),
            'operation': Color(self.operation, 'red'),
            'key_list': Color(self.keylist, 'red')
        }
        return color_error_mesg(mesg, kwds, nocolor)


class IndexOfOfRange(JsonCutError, IndexError):
    """The key or index was not found in the JSON document."""

    def __init__(self, exc, op=None, itemnum=0, data=None, keylist=None):
        """Initialize KeyNotFound Exception.

        Kwds:
            fn (str): name of module/funct where exception was raised
            item (self):  JSON data from which the key was missing
        :param keylist: a list of available keys
        """
        msg = str(exc)
        super(KeyNotFound, self).__init__(msg)
        self.operation = op
        self.item_number = itemnum
        self.data = data
        self.keylist = keylist

    def format_error(self, nocolor=False):
        mesg = (
            '{dashed_line}\n'
            'IndexOutOfRange: {key_name}\n'
            '{dashed_line}\n'
            'Operation: {operation}\n'
            'Item #: {item_number}\n'
            'Parsed Key List: {key_list}\n'
            '{dashed_line}\n'
            'Available Keys:\n'
            '{dashed_line}\n'
            '{available_keys}\n'
        )
        name = self.args[0]
        key_name = name[1:-1] if len(name) > 2 else name
        available_keys = '\n'.join(list(core.list_keys(self.data)))
        kwds = {
            'index_number': Color(key_name, '*red'),
            'dashed_line': Color('-' * 39, 'yellow'),
            'item_number': Color(self.item_number, 'red'),
            'operation': Color(self.operation, 'red'),
            'available_keys': Color(available_keys, 'white'),
            'key_list': Color(self.keylist, 'red')
        }
        return color_error_mesg(mesg, kwds, nocolor)


class KeyNotFound(JsonCutError, KeyError):
    """The key or index was not found in the JSON document."""

    def __init__(self, exc, op=None, itemnum=0, data=None, keylist=None):
        """Initialize KeyNotFound Exception.

        Kwds:
            fn (str): name of module/funct where exception was raised
            item (self):  JSON data from which the key was missing
        :param keylist: a list of available keys
        """
        msg = str(exc)
        super(KeyNotFound, self).__init__(msg)
        self.operation = op
        self.item_number = itemnum
        self.data = data
        self.keylist = keylist

    def format_error(self, nocolor=False):
        mesg = (
            '{dashed_line}\n'
            'KeyNotFound: {key_name}\n'
            '{dashed_line}\n'
            'Operation: {operation}\n'
            'Item #: {item_number}\n'
            'Parsed Key List: {key_list}\n'
            '{dashed_line}\n'
            'Available Keys:\n'
            '{dashed_line}\n'
            '{available_keys}\n'
        )
        name = self.args[0]
        key_name = name[1:-1] if len(name) > 2 else name
        available_keys = '\n'.join(list(core.list_keys(self.data)))
        kwds = {
            'key_name': Color(key_name, '*red'),
            'dashed_line': Color('-' * 39, 'yellow'),
            'item_number': Color(self.item_number, 'red'),
            'operation': Color(self.operation, 'red'),
            'available_keys': Color(available_keys, 'white'),
            'key_list': Color(self.keylist, 'red')
        }
        return color_error_mesg(mesg, kwds, nocolor)
