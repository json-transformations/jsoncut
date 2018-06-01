"""Test JSON Cut main functions."""
from copy import deepcopy

from boltons.iterutils import PathAccessError
import pytest

from jsoncut.core import _UNSET, get_value, set_value
from jsoncut.errors import PathAssignmentError

_data = {
  "source": {
    "name": "Asterank",
    "url": "http://www.asterank.com/api"
  }, "asteroids": [
    {"name": "Ryugu", "type": "Cg", "value $": 82760000000},
    {"name": "1989 ML", "type": "X", "value $": 13940000000},
    {"name": "Nerus", "type": "Xe", "value $": 4710000000}
  ]
}
errors = [
    (('missing', 'key'), KeyError),
    (('asteroids', 8), IndexError),
    (('source', 8), TypeError),
    (('asteroid', 'name'), TypeError)
]
slices = [
    (('asteroids', slice(1, None)), _data['asteroids'][1:]),
    (('asteroids', slice(None, 2)), _data['asteroids'][:2]),
    (('asteroids', slice(1, 2)), _data['asteroids'][1:2]),
    (('asteroids', slice(None, None, 2)), _data['asteroids'][::2]),
]
paths = [
    (('asteroids', slice(1, 2), 0, 'name'), '1989 ML')
]


@pytest.fixture
def data():
    return _data


@pytest.mark.get_value
@pytest.mark.parametrize('path, error', errors)
def test_get_errors(path, error, data):
    with pytest.raises(error):
        get_value(path, data, _UNSET)


@pytest.mark.get_value
def test_get_default(data):
    assert get_value(('missing', 'key'), data) is None


@pytest.mark.get_value
def test_get_index_error(data):
    assert get_value(('asteroids', 8), data) is None


@pytest.mark.get_value
@pytest.mark.parametrize('path, error', errors)
def test_get_type_error(path, error, data):
    if error == TypeError:
        assert get_value(path, data) is None


@pytest.mark.get_value
def test_get_key_names(data):
    print(data)
    assert get_value(('source', 'name'), data) == 'Asterank'


@pytest.mark.set_value
def test_get_index(data):
    assert get_value(('asteroids', 0, 'name'), data) == 'Ryugu'


@pytest.mark.set_value
@pytest.mark.parametrize('slice_, expect', slices)
def test_get_slice(slice_, expect, data):
    assert get_value(slice_, data) == expect


@pytest.mark.set_value
@pytest.mark.parametrize('path, expect', paths)
def test_get_nested_value(path, expect, data):
    assert get_value(path, data) == expect


@pytest.mark.set_value
def test_get_value():
    data = {'results': {'rows': [{}, {}]}}
    result = get_value(('results', 'rows'), data)
    expect = [{}, {}]
    assert result == expect


@pytest.mark.set_value
def test_set_value_missing_key_with_error_suppression(data):
    result = set_value(('missing', 'key'), None, data)
    assert result == data


@pytest.mark.set_value
def test_set_value_path_access_error(data):
    with pytest.raises(PathAccessError):
        set_value(('missing', 'key'), None, data, suppress=False)


@pytest.mark.set_value
def test_set_value_path_assignment_error(data):
    with pytest.raises(PathAssignmentError):
        set_value(('source', 'name', 'key'), None, data, suppress=False)


@pytest.mark.skip
def test_set_value_index_out_of_range(data):
    result = set_value(('asteroids', 8), {}, data)
    assert result == data


@pytest.mark.skip
def test_set_value_type_error(data):
    result = set_value(('source', 8), 'test', data)
    assert result['source'][8] == 'test'


@pytest.mark.set_value
def test_set_value_names(data):
    expect = deepcopy(data)
    result = set_value(('source', 'name'), 'test', data)
    expect['source']['name'] = 'test'
    assert result['source']['name'] == 'test' and result == expect


@pytest.mark.set_value
def test_set_value_index_number(data):
    expect = data
    result = set_value(('asteroids', 0, 'name'), 'test', data)
    expect['asteroids'][0]['name'] = 'test'
    assert result['asteroids'][0]['name'] == 'test' and result == expect


@pytest.mark.skip
@pytest.mark.parametrize('slice_, _', slices)
def test_get_value_slice(slice_, _, data):
    key, slice_ = slice_
    expect = deepcopy(data)
    value = ['test'] if isinstance(slice_, slice) else 'test'
    result = set_value(key, slice_, value, data)
    expect[key][slice_] = value
    assert result == expect


@pytest.mark.set_value
def test_get_value_slice_in_middle(data):
    expect = deepcopy(data)
    result = set_value(('asteroids', slice(1, 2), 0, 'name'), 'test', data)
    expect['asteroids'][1:2][0]['name'] = 'test'
    assert result['asteroids'][1:2][0]['name'] == 'test' and result == expect


@pytest.mark.skip
def test_delete_value(data):
    pass


@pytest.mark.skip
def test_get_values(data):
    pass


@pytest.mark.skip
def test_get_paths(data):
    pass


'''
TEST_DATA = {
    'info': 'test',
    'results': [
        {
            'id': 1719,
            'via': {
                'channel': 'email',
                'source': {
                    'from': {'name': 'John Doe'}
                }
            }
        },
        {
            'id': 1720,
            'via': {
                'channel': 'email',
                'source': {
                    'from': {'name': 'Jane Doe'}
                }
            }
        }
    ]
}

PRUNED_TEST_DATA = [
    {
        'id': 1719,
        'source': {'from': {}}
    },
    {
        'id': 1720,
        'source': {'from': {}}
    }
]


def test_cut():
    """Test core.cut()."""
    rootkey = 'results'
    getkeys = 'id, via.source'
    delkeys = 'source.from.name'
    result = jsoncut.core.cut(TEST_DATA, rootkey=rootkey, getkeys=getkeys,
                              delkeys=delkeys)
    assert result == PRUNED_TEST_DATA
'''
