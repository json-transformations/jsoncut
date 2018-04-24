"""JSON Cut.

json
    Any Python object that can be serialized as JSON.

keylist
    A sequence of key names (str), numbers (int), and/or slices (slice).

keystring
    A keylist represented as a CSV string; supports:
        * key names
        * key numbers
        * key number ranges
        * slices

key
    A keylist or keystring.

node
    A JSON Node; a namedtuple with the following elements:
        1. keylist
        2. val
        3. dtype (data type)

fullpath
    If set, the target's a keystring; otherwise, last key in keylist.

ignore
    A tuple of exceptions to suppress; if suppressed the default value
    is returned..

wildcard
    A symobol used in keys to indicate all elements of an array.
"""

from . import core
from . import exceptions
from . import highlighter
from . import inspector
from . import sequencer
from . import tokenizer
from . import treecrawler

__version__ = '0.6'
