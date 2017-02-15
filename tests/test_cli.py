import json

import click
# import pytest
from click.testing import CliRunner

# import core
# from exceptions import JsonDecodeError, UnableToLoadFile

"""
click.command()
@click.argument('jsonfile', type=click.File())
@click.option('-r', '--root', 'rootkey', help='set the root key/index')
@click.option('-g', '--get', 'getkeys', help='select properties')
@click.option('-G', '--getdefault', type=(str, str), multiple=True,
              help='get property; set to default value if not found')
@click.option('-d', '--del', 'delkeys', help='drop properties')
@click.option('-l', '--list', 'listkeys', is_flag=True, help='list properties')
@click.option('-i', '--inspect', is_flag=True, help='show keys & indexes')
@click.option('-f', '--fullscan', is_flag=True, help='deep key path scan')
@click.option('-p', '--fullpath', is_flag=True, help='preserve full path name')
@click.option('-q', '--quotechar', default='"', help='quote used w/ key names')
"""
TEST_DATA = {
    'results': {
        'tickets': [
            {'id': 1, 'name': 'ticket 1', 'status': 'open'},
            {'id': 2, 'name': 'ticket 2', 'status': 'closed'}
        ]
    }
}

FILTERED_TEST_DATA = [
    {'id': 1},
    {'id': 2}
]


def test_jsonfile_argument():
    @click.command()
    @click.argument('jsonfile', type=click.File())
    def main(jsonfile, **kwds):
        click.echo(jsonfile.read())

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_data = json.dumps(TEST_DATA)
        with open('test.json', 'w') as f:
            f.write(test_data)

        result = runner.invoke(main, ['test.json'])
        assert result.exit_code == 0

        data = json.loads(result.output.replace("'", '"'))
        assert data == TEST_DATA
