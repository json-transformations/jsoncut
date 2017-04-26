"""JSON sytax highligting.

Pygments is used for JSON syntax highlighting, but is only an optional
dependency for JSON Cut.

+-----------------------+
| Supported ANSI colors |
+-----------+-----------+
| black     | darkgray  |
| darkred   | red       |
| darkgreen | green     |
| brown     | yellow    |
| darkblue  | blue      |
| purple    | fuschsia  |
| teal      | turquoise |
| lightgray | white     |
+-----------+-----------+
https://github.com/nex3/pygments/blob/master/pygments/formatters/terminal.py
"""
import json
from functools import reduce

try:
    import pygments
    from pygments.formatters import TerminalFormatter
    from pygments.lexers import JsonLexer
except ImportError:
    pass

STYLE = dict(Token='darkgray', Keyword='brown', Name_Tag='darkgreen',
             String='lightgray', Number='fuchsia')


def get_style(style=STYLE):
    """Load Pygments custom style."""
    def getattrs(obj, names):
        return reduce(getattr, names.split('_'), obj)
    return {getattrs(pygments.token, k): (v,) * 2 for k, v in style.items()}


def format_json(d, compact=False, indent=2):
    """Format JSON; compact or indented."""
    separators = (',', ':') if compact else None
    return json.dumps(d, indent=indent, separators=separators)


def highlight_json(d, style=STYLE):
    """JSON Syntax highlighter."""
    try:
        formatter = TerminalFormatter(colorscheme=get_style(style))
    except (NameError, AttributeError):
        return d
    return pygments.highlight(d, JsonLexer(), formatter)
