"""Parse key path names, key numbers and ranges.

The quotechar is particularly handy for Windows command-lines where
the doublequotes are use for string arguments with spaces/special
characters.  By allowing the user to set the quotechar to single-quotes
the won't need to escaped any doublequotes around key names.
 key names then you won't need
to use quotes around key names and none of this matters.

If the user puts spaces after the commas this function will
ignore them, the command-line will still intrepret the spaces
separate arguments unless it is quoted.
"""
import ast
import csv
import io
import re

from . import exceptions as exc
from .treecrawler import find_keys

SLICE_RE = re.compile(r'[-\d:]+$')
UNESCAPED_DOT_RE = re.compile(r'(?<!\\)\.')
NUMBER_RANGE_RE = re.compile(r'[-:\d]+$')

csv.register_dialect('JsonKeys', delimiter=',', strict=False,
                     quoting=csv.QUOTE_MINIMAL, doublequote=False,
                     escapechar='\\', skipinitialspace=True)


def parse_csv(s, quotechar='"'):
    r"""Parse CSV values in string using specified dialect & quotechar.

    Args:
        s (str): Comma-separated JSON Keys
        quotechar (str): Single or double-quote character around JSON
            Keys, useful for different command-line environments
            (i.e. Windows) that handle quoting differently; eliminates
            having to escape quote characters around JSON Keys. Note:
            The parser supports minimal quoting, so quotes are only
            required when key names contain spaces or special
            characters.

    Returns:
        List[str]: List of JSON Keys

    Examples:
        >>> parse_csv("key1.key2,key3")
        ['key1.key2', 'key3']

        >>> parse_csv('key1.key2, "key w/ non-alphanums", key3')
        ['key1.key2', 'key w/ non-alphanums', 'key3']

        >>> parse_csv("key1.key2, \"w/ non-alphanums\", key3")
        ['key1.key2', 'w/ non-alphanums', 'key3']

        >>> parse_csv("key1.key2, 'w/ non-alphanums', key3", quotechar="'")
        ['key1.key2', 'w/ non-alphanums', 'key3']
    """
    return next(csv.reader(io.StringIO(s), 'JsonKeys', quotechar=quotechar))


def parse_key_name(key):
    r"""Parse Key Path.

    Args:
        name (str): JSON Key.

    Returns:
        Tuple(str): List of key names, indexes or slice strings used to
            form the JSON key.

    Example:
        >>> parse_key_path('.k 1.k\\.2.k3')
        ('k 1', 'k.2', 'k3')

    Notes:
        * Key paths are specified using dots as separators.
        * Precede a dot with a backslash to preserve '.' as a literal.
        * Any leading dot characters are stripped.
   """
    keys = UNESCAPED_DOT_RE.split(key.lstrip('.'))
    return tuple(i.replace('\\.', '.') for i in keys)


def parse_key_number(token, items):
    """Parse key number or range.

    *nix cut style number ranges; also supports using colons instead
    of dashes to separate ranges.  Note: the colons are treated the
    same as dashes

    Args:
        tokens: List[str] a list of numbers or number ranges.

    Yields:
        str: key names corresponding to the numbers/ranges.

    Raises:
        KeyNumberOutOfRange

    Examples:
        >>> items = ['i1', 'i1.i2', 'i1.i2.i3', 'i4']

        >>> list(parse_key_range(['1'], items))
        [['i1']]

        >>> list(parse_key_range(['2-'], items))
        [['i1.i2', 'i1.i2.i3', 'i4']]

        >>> list(parse_key_range(['-3'], items))
        [['i1', 'i1.i2', 'i1.i2.i3']]
    """
    try:
        endpts = [int(i) if i else None for i in token.split('-', 1)]
        if any(i for i in endpts if not (i is None or 0 < i <= len(items))):
            raise ValueError
    except ValueError:
        raise exc.KeyNumberOutOfRange(token)
    if endpts[0] is not None:
        endpts[0] -= 1
    if len(endpts) == 1:
        endpts = (endpts[0], endpts[0] + 1)
    return [parse_key_name(i) for i in items[slice(*endpts)]]


def parse_defaults(keystr, value, **kwds):
    """Parse defaults."""
    def parse_value(v):
        try:
            print(v)
            return ast.literal_eval(v)
        except (ValueError, SyntaxError):
            return v

    return parse_keystr(keystr, **kwds), parse_value(value)


def parse_keys(tokens, keys):
    """Parse keys."""
    for token in tokens:
        if NUMBER_RANGE_RE.match(token):
            for keylist in parse_key_number(token, keys):
                yield keylist
        else:
            yield parse_key_name(token)


def parse_keystr(keystr, data=None, quotechar='"', keys=None, fullscan=False):
    """Parse Keys.

    Args:
        keystr (str): attr-style key names/paths or key numbers/ranges.
        d (Mapping or Sequence): JSON encodable data (document)
        quotechar (str): type of quote used to surrounds key names with
            special characters.
        keys (List[str]): list of key path names found in data.
        fullscan (bool): crawl through all key paths; revisit key names
            see docs for additional details.

    Returns:
        List[List[str]]: list of JSON Key lists
    """
    tokens = parse_csv(keystr, quotechar)
    if any(NUMBER_RANGE_RE.match(i) for i in tokens):
        if keys is None:
            keys = find_keys(data, fullscan)
    return list(parse_keys(tokens, keys))
