"""Command-Line Interface."""

import json
import sys

import click
from click import argument, option, version_option

from . import core
from . import exceptions as exc
from . import highlighter
from . import treecrawler


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


def click_options(ctx):
    '''
    Build and return a dictionary with the variable name from click
    and the associated option used from the command line, for each
    available option defined by the click.option decorator
    ie. {'rootkey':'root'}

    :param ctx: click context object
    :return: dictionary
    '''
    return {opt.human_readable_name: opt.opts[1]
            for opt in ctx.command.get_params(ctx)
            if isinstance(opt, click.Option) and len(opt.opts) > 1}


def validate_numeric(kwd_value, split_char=','):
    '''
    Helper function to verify that the kwd_value is a numeric string.
    The string could be comma separated, and each individual value is also checked.

    Raises: KeyNotNumeric

    :param kwd_value: string
    :return: None
    '''

    for value in kwd_value.split(split_char):
        if not value.isdigit():
            raise exc.KeyNotNumeric(value)

def expand(data, ctx, kwds):
    '''
    Return an expanded version of a series of command line arguments,
    to allow the user to interactively transform data and then see
    the long version of the same command with any key numbers replaced
    with their respective key names.

    Examples:
    jsoncut -e -r2  -g1,2 tests/sample_data/quakes.json
    to
    jsoncut --root features --get geometry.coordinates,geometry.type /
    --quotechar '"' tests/sample_data/quakes.json

    :param data:
    :param ctx:
    :param kwds:
    :return:
    '''

    expanded_args = [sys.argv[0]]
    options = click_options(ctx)
    keylist = treecrawler.find_keys(data)

    # Ensure that these values are all numeric, a requirement for the expand option.
    try:
        if kwds['rootkey']:
            validate_numeric(kwds['rootkey'], '.')
    except exc.JsonCutError as e:
        expanded_args.append('--root ' + kwds['rootkey'])
        kwds['rootkey'] = False

    try:
        if kwds['getkeys']:
            validate_numeric(kwds['getkeys'][0])
    except exc.JsonCutError as e:
        click.echo(e.format_error(), err=True)
        sys.exit(1)


    if kwds['rootkey']:
        kwds['rootkey'] = keylist[int(kwds['rootkey'])-1]
        keylist = treecrawler.find_keys(
            core.get_rootkey(data, kwds['rootkey']))

    for k, v in kwds.items():

        if k in ['jsonfile', 'expand']:
            continue
        if v:
            value = ''
            if k == 'quotechar':
                value = "'" + v + "'"
            elif k == 'getkeys':
                values = []
                # v is a tuple, we need to convert the string to a list
                # and find the corresponding expanded value
                for i in v[0].split(','):
                    values.append(keylist[int(i)])
                value = ','.join(values)
            else:
                value = v

            arg = options[k] if value is True else options[k] + ' ' + value

            expanded_args.append(arg)

    expanded_args.append(kwds['jsonfile'])

    return [' '.join(expanded_args)]


def cut(data, kwds):
    kwds_copy = kwds.copy()
    for key in ('getkeys', 'delkeys'):
        kwds_copy[key] = ','.join(kwds_copy[key])
    for key in ('compact', 'jsonfile', 'nocolor', 'expand'):
        del kwds_copy[key]
    try:
        return core.cut(data, **kwds_copy)
    except exc.JsonCutError as e:
        click.echo(e.format_error(), err=True)
        sys.exit(1)


def output(ctx, output, compact, is_json):
    try:
        if not is_json:
            for key in output:
                click.echo(key)
        elif output:
            output = highlighter.format_json(output, compact, 2)
            if ctx.color and sys.stdout.isatty():
                output = highlighter.highlight_json(output)
            click.echo(output)
    except KeyboardInterrupt:
        sys.exit(0)


@click.command()
@argument('jsonfile', type=click.Path(readable=True), required=False)
@option('-r', '--root', 'rootkey', help='Set the root of the JSON document')
@option('-g', '--get', 'getkeys', multiple=True,
        help='Get JSON key-values and/or elements')
@option('-G', '--getdefault', 'getdefaults', type=(str, str), multiple=True,
        help=('(key, default-value); same as get, except uses a default value'
              'when the key or index is not found'))
@option('-d', '--del', 'delkeys', multiple=True,
        help='Delete JSON keys and/or indexes')
@option('-l', '--list', 'listkeys', is_flag=True,
        help='Numbered JSON keys list')
@option('-i', '--inspect', is_flag=True,
        help='Inspect JSON document; all keys, indexes & types')
@option('-c', '--count', is_flag=True,
        help='Count elements in top-level JSON arrays')
@option('-f', '--fullscan', is_flag=True, help='Deep inspections')
@option('-p', '--fullpath', is_flag=True, help='Preserve full path for names')
@option('-q', '--quotechar', default='"', help='Set quoting char for keys')
@option('-C', '--compact', default=False, help='Compacts the JSON output')
@option('-n', '--nocolor', is_flag=True, help='Disable syntax highlighting')
@option('-s', '--slice', 'slice_', is_flag=True, help='Disable sequencer')
@option('-e', '--expand', is_flag=True,
        help='Expand key numbers to key names')
@version_option(version='0.6', prog_name='JSON Cut')
@click.pass_context
def main(ctx, **kwds):
    """Quickly select or filter out properties in a JSON document."""
    ctx.color = False if kwds['nocolor'] else True
    data = load_json(ctx, kwds['jsonfile'])
    results = cut(data, kwds)
    if results:
        is_json = not (kwds['listkeys'] or kwds['inspect'] or kwds['count'])
        output(ctx, results, kwds['compact'], is_json)
        if kwds['expand']:
            output(ctx, expand(data, ctx, kwds), False, False)


if __name__ == '__main__':
    main()
