"""Command-Line Interface."""

import json
import sys

import click
from click import argument, option, version_option

from . import core
from . import exceptions as exc
from . import highlighter


def load_json(ctx, filename):
    if filename is None:
        if sys.stdin.isatty():
            click.echo(ctx.get_usage())
            click.echo("Try `jsoncut --help' for more information.")
            sys.exit(0)
        else:
            filename = '-'
    try:
        with click.open_file(filename) as file_:
            return json.load(file_)
    except EnvironmentError as e:
        if not sys.stdin.isatty():
            sys.stdin.read()
        click.echo(exc.default_error_mesg_fmt(e), err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(exc.default_error_mesg_fmt(e), err=True)
        sys.exit(1)


def cut(data, kwds):
    kwds_copy = kwds.copy()
    for key in ('indent', 'jsonfile', 'nocolor'):
        del kwds_copy[key]
    try:
        return core.cut(data, **kwds_copy)
    except exc.JsonCutError as e:
        click.echo(e.format_error(), err=True)
        sys.exit(1)


def output(ctx, output, indent, is_json):
    try:
        if not is_json:
            for key in output:
                click.echo(key)
        elif output:
            if sys.stdout.isatty():
                compact = False
                indent = 2 if indent is None else indent
            else:
                compact = indent is None
            output = highlighter.format_json(output, compact, indent)
            if ctx.color and sys.stdout.isatty():
                output = highlighter.highlight_json(output)
            click.echo(output)
    except KeyboardInterrupt:
        sys.exit(0)


@click.command()
@argument('jsonfile', type=click.Path(readable=True), required=False)
@option('-r', '--root', 'rootkey', help='Set the root of the JSON document')
@option('-g', '--get', 'getkeys', help='Get JSON key-values and/or elements')
@option('-G', '--getdefault', 'getdefaults', type=(str, str), multiple=True,
        help=('(key, default-value); same as get, except uses a default value'
              'when the key or index is not found'))
@option('-d', '--del', 'delkeys', help='delete JSON keys and/or indexes')
@option('-a', '--any', is_flag=True, default=True,
        help='get/del any matching keys; supress key not found errors.')
@option('-l', '--list', 'listkeys', is_flag=True,
        help='numbered JSON keys list')
@option('-i', '--inspect', is_flag=True,
        help='inspect JSON document; all keys, indexes & types')
@option('-c', '--count', is_flag=True,
        help='count elements in top-level JSON arrays')
@option('-F', '--flatten', 'flatten',
        help='flatten the JSON document for specified keys, flattens all ' +
        'keys if argument set to 0')
@option('-f', '--fullscan', is_flag=True, help='deep inpections')
@option('-p', '--fullpath', is_flag=True, help='preserve full path for names')
@option('-q', '--quotechar', default='"', help='set quoting char for keys')
@option('-I', '--indent', type=int, help='indent JSON when redirecting')
@option('-n', '--nocolor', is_flag=True, help='disable syntax highlighting')
@option('-s', '--slice', 'slice_', is_flag=True, help='disable sequencer')
@version_option(version='0.4', prog_name='JSON Cut')
@click.pass_context
def main(ctx, **kwds):
    """Quickly select or filter out properties in a JSON document."""
    ctx.color = False if kwds['nocolor'] else True
    data = load_json(ctx, kwds['jsonfile'])
    results = cut(data, kwds)
    if results:
        is_json = not (kwds['listkeys'] or kwds['inspect'] or kwds['count'])
        output(ctx, results, kwds['indent'], is_json)


if __name__ == '__main__':
    main()
