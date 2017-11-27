"""JSON Keys core functions.

JSON Key definition:
    An ordered sequence of one or more JSON pointer reference tokens
    (Object member key or array index) starting with a root-level
    key/index and ending with a reference to some value within the
    document.

    The last key can optionally be Python slice syntax, where # can
    zero, a positive or negative integer:
        ':', '#:', ':#', '#:#', '::#', '#::#', ':#:#' or '#:#:#'

    Keys are joined together by dot characters.

    Examples:
        name
        name.last
        names.0.name.last
        names.2:5
"""
from copy import deepcopy
from functools import reduce
from operator import getitem

import click

from . import exceptions as exc
from .inspector import inspect_json, count_arrays
from .sequencer import Items
from .tokenizer import SLICE_RE, parse_defaults, parse_keystr
from .treecrawler import find_keys


def get_rootkey(d, *keys):
    """Set the root level of the JSON document.

    Purpose:
        1. Point to an array of objects within the JSON document so that
           get, del and friends will operate on the properties for each
           item in the JSON array.
        2. Extract a single branch or value from a JSON document.

    Args:
        d (Mapping or Sequence): JSON encodable data (document.)
        *keys (str): JSON Keys (name, index or trailing slice.)

    Returns:
        The value referenced by *keys.

    Raises:
        KeyNotFound
        IndexError
        TypeError

    Example:
        >>> d = {'results': {'rows': [{}, {}]}}
        >>> get_rootkey(d, 'results', 'rows')
        [{}, {}]
    """
    try:
        return select_key(d, *keys)
    except KeyError as e:
        raise exc.KeyNotFound(e, op='rootkey', data=d, keylist=[keys])
    except IndexError as e:
        raise exc.IndexOutOfRange(e, op='rootkey', data=d, keylist=[keys])
    except TypeError as e:
        raise exc.KeyTypeError(e, op='rootkey', data=d, keylist=[keys])


def list_keys(d, fullscan=False, fg_nums='yellow'):
    """Generate numbered, sorted list of keys found in JSON document.

    Purpose:
        1. Show available JSON keys.
        2. Show key #'s for JSON Keys; used as a shorthand for names.
           Using key numbers makes JSON Cut feel more like the way the
           *nix cut command works for tabular data.

    List crawls through keys looking for new key names. It does not
    crawl through Sequences (JSON arrays); with the exception of an
    array located at the root-level of the document.

    Args:
        d (Mapping or Sequence): JSON encodable data (document)
        fullscan (bool): traverse all keys looking for new ones;
            default is to skip over previously visited key pointers.
        fg_nums (str): a 'click' supported foreground color name used
            to highlight the numbers and create a visual separation
            between numbers and values (the values will be white.)
            Supported color names: red, green, yellow, blue, magenta,
            cyan, white.

    Returns:
        List[str]: sorted, numbered list of JSON keys found in document.

    See also:
        treecrawler module

    Examples:
        >>> d = [{'k1': {'k2': []}, 'k3': None}, {'k1': {'k4': []}}]

        >>> for key in list_keys(d):
        ...     click.echo(key, color=None)
        1 k1
        2 k1.k2
        3 k3

        Note: In the above example fullscan=False, 'k1.k4' does not show
        up that is because the key selector 'k1' has already been
        visited when it evalutes the 2nd item in the array, so it skips
        crawling through the child nodes in this 2nd instance.

        >>> for key in list_keys(d, fullscan=True):
        ...     click.echo(key, color=None)
        1 k1
        2 k1.k2
        3 k1.k4
        4 k3

        Note: When fullscan=True the function will crawl through all
        JSON objects looking for any new keys; even if the same full key
        selector name has been previosuly visited.

        >>> d = {'k1': {'k2': [{'k3': None}]}, 'k4': 5}
        >>> for key in list_keys(d, fullscan=True):
        ...     click.echo(key, color=None)
        1 k1
        2 k1.k2
        3 k4

        The reason is that it that --list option enumerates items so
        that they can be used as
        a quick way of specifying JSON selectors from the command-line;
        supporting
        enumerated keys nested inside of nested indexes adds unnecesary
        complexity, and at least to this point there haven't been any
        real-world use cases to justify the need for such as feature.

        Note: You can still crawl through nested keys in nested indexes
        and view them using --inspect, you can also access them
        explicitly
        using key names & indexes, you just can't treat the results as
        numbered shortcuts as you do with --list for specifying key
        paths in the command-line.
    """
    keys = find_keys(d, fullscan)
    padding = len(str(len(keys)))
    numbers = (str(i).rjust(padding) for i in range(1, len(keys) + 1))
    numbers = (click.style(i, fg=fg_nums) for i in numbers)
    return (n + ' ' + i for n, i in zip(numbers, keys))


def get_item(d, key):
    """Try to get item using the key, if fails try as an index or slice.

    Args:
        d (Mapping or Sequence): JSON encodable data (document)
        key (str): JSON Keys.

    Returns:
        The key's value retrieved from the provided data (document)

    Raises:
        KeyError
        IndexError
        TypeError

    Examples:
        >>> get_item({'0': 'a key'}, '0')
        'a key'

        >>> get_item(['an index'], '0')
        'an index'
    """
    try:
        return getitem(d, key)
    except TypeError:
        if key.isdigit():
            return getitem(d, int(key))
        if SLICE_RE.match(key):
            if ':' not in key:
                return d[int(key)]
            return d[slice(*(int(i) if i else None for i in key.split(':')))]
        raise


def select_key(d, *keys, default=None, no_default=False):
    """Get a nested value in a Mapping given the list of keys.

    Args:
        d (Mapping or Sequence): JSON encodable data (document)
        *keys (str): JSON Keys (name, index or trailing slice)
        default: Default value if key or index is not found.
        no_default (bool): If True, raise KeyNotFound when the key is
            not found or the index is out of range otherwise it uses
            the 'default' value.

    Returns:
        The value in the document pointed to by the JSON keys.

    Raises:
        KeyNotFound: Only returned if no_default option is set.
        KeyTypeError: When trying to use a key on a Sequence
            or an index on a Mapping.
        IndexOutOfRange: When trying to use an index number that
            greater than the length of the Sequence.

    Examples:
        >>> d = {'k1': {'k2': 'Found Key/Value'}}
        >>> select_key(d, 'k1', 'k2')
        'Found Key/Value'

        >>> print(select_key(d, 'k1', 'missing key')
        None

        If no_default is True it will raise a KeyNotFound error.
        >>> select_key(d, 'k1', 'missing key', default='Default Value')
        'Default Value'

        >>> d = {'k1': [{'k2': 'Found Index/Value'}]}
        >>> select_key(d, 'k1', '0', 'k2')
        'Found Index/Value Value'
    """
    try:
        return reduce(get_item, keys, d)
    except KeyError as e:
        if no_default:
            raise exc.KeyNotFound(e)
        return default
    except IndexError as e:
        raise exc.IndexOutOfRange(e)
    except TypeError as e:
        raise exc.KeyTypeError(e)


def into_key(*keys, fullpath=False):
    """Generate target key name for the data.

    Args:
        *keys (str): JSON Keys (name, index or trailing slice)
        fullpath (bool): Use the full JSON Key path for the target name.

    Returns:
        str: Key name to store the data in.

    Examples:
        >>> into_key(['k1', 'k2'])
        'k2'
        >>> into_key(['k1', 'k2'], fullpath=True)
        'k1.k2'
    """
    return '.'.join(keys) if fullpath else keys[-1]


def get_items(d, *keylists, fullpath=False, any=True, n=0):
    """Get multiple nested items from a dict given the keys.

    Args:
        d (Mapping or Sequence): JSON encodable data (document)
        *keylists List[str]: JSON Keys (name, index or trailing slice)
        fullpath (bool): Use the full JSON Key path in the target name.
        any (bool): If True get any instance of the JSON Key value that
            exists; otherwise raise KeyNotFound if the key is missing.
        n (int): Data item number being processed; shown to user in
            exception handling.

    Returns:
        dict: All Key/Values in data referenced by JSON Keys

    Raises:
        KeyNotFound: Only returned if 'any' option is not set.
        KeyTypeError: When trying to use a key on a Sequence
            or an index on a Mapping.
        IndexOutOfRange: Only returned if 'any' option is not set.

    Examples:
        >>> d = {'k1': {'k2': 'item1'}, 'k3': 'item2'}
        >>> get_items(d, ['k1', 'k2'], ['k3'])
        {'k2': 'item1', 'k3': 'item2'}

        >>> get_items(d, ['k1', 'k2'], ['k3'], fullpath=True)
        {'k1.k2': 'item1', 'k3': 'item2'}
    """
    result = {}
    for keylist in keylists:
        try:
            into = into_key(*keylist, fullpath=fullpath)
            result[into] = select_key(d, *keylist, no_default=True)
        except exc.KeyNotFound as e:
            if not any:
                kwds = dict(op='get', itemnum=n, data=d, keylist=keylists)
                raise exc.KeyNotFound(e, **kwds)
        except exc.IndexOutOfRange as e:
            kwds = dict(op='get', itemnum=n, data=d, keylist=keylists)
            raise exc.IndexOutOfRange(e, **kwds)
        except exc.KeyTypeError as e:
            kwds = dict(op='get', itemnum=n, data=d, keylist=keylists)
            raise exc.KeyTypeError(e, **kwds)
    return result


def get_defaults(d, *defaults, fullpath=False, n=0):
    """Get nested items from keys, set default value if key not found.

    Args:
        d (Mapping or Sequence): JSON encodable data (document)
        *defaults (List[Tuple(List[str], str)]):
            (List[str]) - JSON Keys (name, index or trailing slice)
            (str) - A string evaluated as a Python literal (see
                Default Values)

            Python  JSON
            ======  ======
            dict    object
            list    array
            str     string
            int     number
            float   number
            True    true
            False   false
            None    null

        fullpath (bool): Use the full JSON Key path in the target name.
        n (int): Data item number being processed; shown to user in
            exception handling.

    Returns:
        dict: All Key/Values in data referenced by JSON Keys or default
            values when key is not found.

    Raises:
        KeyTypeError: When trying to use a key on a Sequence
            or an index on a Mapping.

    Examples:
        >>> d = {'k1': {'k2': 'item1'}}
        >>> defaults = [(['k1', 'k2'], None), (['k3'], False)]

        >>> get_defaults(d, *defaults)
        {'k2': 'item1', 'k3': False}

        >>> get_defaults(d, *defaults, fullpath=True)
        {'k1.k2': 'item1', 'k3': False}
    """
    try:
        return {into_key(k, fullpath): select_key(d, *k, default=v)
                for k, v in defaults}
    except exc.KeyTypeError as e:
        kwds = dict(op='getdefaults', data=d, keylists=defaults)
        raise exc.KeyTypeError(e, **kwds)


def drop_key(d, *keys, no_key_error=True):
    """Delete nested item from Mapping or Sequence given list of keys.

    Args:
        d (Mapping or Sequence): JSON encodable data (document)
        *keylists List[str]: JSON Keys (name, index or trailing slice)
        no_key_error (bool): If True, ignore Key Errors.

    Raises:
        KeyError
        IndexError
        TypeError

    Examples:
        >>> d = {'k1': {'k2': 'Deleted!'}}
        >>> drop_key(d, 'k1', 'k2')
        >>> d
        {'k1': {}}

        >>> d = {'k1': [{'k2': 'Deleted!'}]}
        >>> drop_key(d, 'k1', 0)
        >>> d
        {'k1': []}

        >>> d = ['As an index']
        >>> drop_key(d, '0')
        >>>
        []

        >>> d = ['As an index']
        >>> drop_key(d, '0')
        >>>
        []
    """
    parent = d if len(keys) == 1 else select_key(d, *keys[:-1])
    try:
        del parent[keys[-1]]
    except (KeyError, IndexError):
        if not no_key_error:
            raise
    except TypeError:
        key = keys[-1]
        if key.isdigit():
            del parent[int(key)]
        elif SLICE_RE.match(key):
            del parent[slice(key.split(':'))]
        else:
            raise


def del_items(d, *keylists, any=False, n=0):
    """Delete multiple nested items from a dict using lists of keys.

    Args:
        d (Mapping or Sequence): JSON encodable data (document)
        *keylists List[str]: JSON Keys (name, index or trailing slice)
        any (bool): If True delete any instance of the JSON Key value
            that exists; if False, raise KeyNotFound error if the key
            is missing.
        n (int): Data item number being processed; shown to user in
            exception handling.

    Raises:
        KeyNotFound: Only returned if 'any' option is not set.
        KeyTypeError: When trying to use a key on a Sequence
            or an index on a Mapping.
        IndexOutOfRange: Only returned if 'any' option is not set.

    Examples:
        >>> d = {'k1': {'k2': 'item1'}, 'k3': 'item2'}
        >>> del_items(d, ['k1', 'k2'], ['k3'])
        >>> d
        {'k1': {}}
    """
    for keylist in keylists:
        try:
            drop_key(d, *keylist, no_key_error=any)
        except KeyError as e:
            if not any:
                kwds = dict(op='del', itemnum=n, data=d, keylist=keylist)
                raise exc.KeyNotFound(e, **kwds)
        except IndexError as e:
            kwds = dict(op='del', itemnum=n, data=d, keylists=keylists)
            raise exc.IndexOutOfRange(e, **kwds)
        except TypeError as e:
            kwds = dict(op='del', itemnum=n, data=d, keylists=keylists)
            raise exc.KeyTypeError(e, **kwds)


def cut(data, rootkey=None, getkeys=None, getdefaults=None, delkeys=None,
        any=False, listkeys=False, inspect=False, count=False, fullpath=False,
        fullscan=False, quotechar='"', slice_=False):
    """Translate the given user data & parameters into actions.

    This function is effectively the hub/core of JSON cut.

    Args:
        data (obj): a JSON encodable object.
        rootkey (str): set the root of the object (JSON Key)
        getkeys (str): select properties (JSON Keys)
        getany (str): select properties (JSON Kyes); ignore if key not
            found.
        getdefaults (List[Tuple(List[str], str)]):
            select properties Tuple(List[JSON Key], Default-Value]);
            use the default value if the key isn't found. Default values
            are strings that are evaluated as Python literals.
        delkeys (str): drop properties (JSON Keys)
        any (bool): If True get/dele any instance of the JSON Key value
            that exists; if False, raise KeyNotFound error if the key
            or index does not exist.
        listkeys (bool): enumerated, sorted list all unique JSON Keys.
        inspect (bool): sorted list of all unique JSON Keys.
        count (bool):
        flatten (str): flatten specified key numbers (output of --list)
        rows (str): generate flattened row data from specified root key
            number (output of --list), optionally prepend each row with
            specified comma-separated key numbers as second argument
        fullpath (bool): used with get*; include the full key name path.
        fullscan (bool): don't skip previously visited JSON Keys.
        quotechar (str): the quote character used around JSON Keys.
        slice (bool): when the document root is an array don't iterate
    """
    if rootkey:
        keylist = parse_keystr(rootkey, data, quotechar, None, fullscan)
        data = get_rootkey(data, *keylist[0])

    if getkeys or getdefaults or delkeys:
        data = Items([data] if slice_ else data)
        items = deepcopy(data.items) if getkeys and getdefaults else data.items
        keys = find_keys(data.value, fullscan)
        full, qchar = fullpath, quotechar

        if getkeys:
            keylists = parse_keystr(getkeys, data.items, quotechar, keys)
            data.items = [get_items(d, *keylists, fullpath=full, any=any, n=n)
                          for n, d in enumerate(data.items, 1)]
        if getdefaults:
            print(getdefaults)
            defaults = getdefaults
            kwds = dict(data=data, quotechar=qchar, keys=keys, fullscan=full)
            defaults = [parse_defaults(i[0], j, **kwds) for i, j in defaults]
            print(defaults)
            for n, item in enumerate(items, 1):
                results = get_defaults(item, *defaults, fullpath=full, n=n)
                data.items[n - 1].update(results)
        if delkeys:
            keylists = parse_keystr(delkeys, data.items, quotechar, keys)
            for item_num, item in enumerate(data.items):
                del_items(item, *keylists, any=any, n=item_num)

        data = data.value

    if inspect:
        return inspect_json(data)
    elif listkeys:
        return list_keys(data, fullscan)
    elif count:
        return count_arrays(data)
    else:
        return data
