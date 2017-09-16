"""
Test module for the jsoncut.flattener fuctions
"""

import pytest

from jsoncut.flattener import flatten_all
from jsoncut.flattener import flatten_by_keys
from jsoncut.flattener import generate_rows
from jsoncut.flattener import get_key_content
from jsoncut.exceptions import KeyNotFound

##############################################################################
# SAMPLE DATA
##############################################################################

SOURCE = {
    'city': 'jacksonville',
    'date': '2017-09-15',
    'coord': {
        'lat': 34,
        'lon': -80,
    },
    'forecast': [{
        'day': 'Monday',
        'temp': {
            'hi': 80,
            'low': 70,
        },
        'wind': {
            'mph': 12,
            'direction': 'ENE',
        },
    },{
        'day': 'Tuesday',
        'temp': {
            'hi': 82,
            'low': 71,
        },
        'wind': {
            'mph': 13,
            'direction': 'S',
        },
    },
    ]
}

SOURCE_FLAT = {
    'city': 'jacksonville',
    'date': '2017-09-15',
    'coord.lat': 34,
    'coord.lon': -80,
    'forecast': [{
        'day': 'Monday',
        'temp.hi' : 80,
        'temp.low' : 70,
        'wind.mph' : 12,
        'wind.direction' : 'ENE'
        },{
        'day': 'Tuesday',
        'temp.hi' : 82,
        'temp.low' : 71,
        'wind.mph' : 13,
        'wind.direction' : 'S'
        },
    ]
}

SOURCE_ROWS = [
    {'city': 'jacksonville',
     'coord.lat': 34,
     'coord.lon': -80,
     'day': 'Monday',
     'temp.hi': 80,
     'temp.low': 70,
     'wind.mph': 12,
     'wind.direction': 'ENE'},
    {'city': 'jacksonville',
     'coord.lat': 34,
     'coord.lon': -80,
     'day': 'Tuesday',
     'temp.hi': 82,
     'temp.low': 71,
     'wind.mph': 13,
     'wind.direction': 'S'},
]


##############################################################################
# TESTS flatten_all
##############################################################################

def test_flatten_all():
    """
    GIVEN a json-serialzed document converted to a python dict
    WHEN the user requests to flatten the entire document
    THEN assert is it flattened and in the correct format
    """
    flattened = flatten_all(SOURCE)
    assert flattened == SOURCE_FLAT


##############################################################################
# TESTS flatten_by_keys
##############################################################################

def test_flatten_by_keys_all():
    """
    GIVEN a json-serialzed document converted to a python dict
    WHEN the user requests to flatten but does not list keys
    THEN assert it flattens the entire document
    """
    flattened = flatten_by_keys(SOURCE)
    assert flattened == SOURCE_FLAT


def test_flatten_by_keys_validList():
    """
    GIVEN a json-serialzed document converted to a python dict
    WHEN the user requests to flatten and specifies a list of keys
    THEN assert it flattens only the specified keys
    """
    flattened = flatten_by_keys(SOURCE, keys=['city', 'coord.lat'])
    assert flattened == {'city': 'jacksonville', 'coord.lat': 34}


def test_flatten_by_keys_KeyNotFound():
    """
    GIVEN a json-serialzed document converted to a python dict
    WHEN the user requests to flatten with a key that does not exist
    THEN assert jsoncut.exceptions.KeyNotFound is raised
    """
    with pytest.raises(KeyNotFound):
        flatten_by_keys(SOURCE, keys=['not.a.real.key'])


##############################################################################
# TESTS generate_rows
##############################################################################

def test_generate_rows():
    """
    GIVEN a json-serialzed document converted to a python dict
    WHEN the user requests to generate rows of data items with prepended
        sources
    THEN assert the rows are generated
    """
    row = generate_rows(SOURCE, 'forecast', ['city',
        'coord.lat', 'coord.lon'])
    assert next(row) == SOURCE_ROWS[0]
    assert next(row) == SOURCE_ROWS[1]


def test_generate_rows_invalid_rootkey():
    """
    GIVEN a json-serialzed document converted to a python dict
    WHEN the user requests to generate rows of data from an invalid root_key
    THEN assert jsoncut.exceptions.KeyNotFound is raised
    """
    with pytest.raises(KeyNotFound):
        next(generate_rows(SOURCE, 'bad_key', ['city']))


def test_generate_rows_invalid_prependkey():
    """
    GIVEN a json-serialzed document converted to a python dict
    WHEN the user requests to generate rows of data from a valid root_key, but
        with invalid prepend_keys
    THEN assert jsoncut.exceptions.KeyNotFound is raised
    """
    with pytest.raises(KeyNotFound):
        next(generate_rows(SOURCE, 'forecast', ['bad_key']))


## NEED MORE TESTS HERE???



##############################################################################
# TESTS get_content
##############################################################################

@pytest.mark.parametrize('key',
    ['city',
    'date',
    'coord.lat',
    'coord.lon',])
def test_get_content_validKey(key):
    """
    GIVEN a json-serialzed document converted to a python dict
    WHEN the user requests the value of a jsoncut-style key
    THEN assert only that key is returned
    """
    content = get_key_content(SOURCE, key)
    assert content == SOURCE_FLAT[key]


def test_get_content_invalidKey():
    """
    GIVEN a json-serialzed document converted to a python dict
    WHEN the user requests to flatten an invalid key
    THEN assert jsoncut.exceptions.KeyNotFound is raised
    """
    with pytest.raises(KeyNotFound):
        get_key_content(SOURCE, 'not.a.real.key')


def test_get_content_keyValidDict():
    """
    GIVEN a json-serialzed document converted to a python dict
    WHEN the user requests to flatten a key whose value is another dict
    THEN assert None is returned
    """
    content = get_key_content(SOURCE['forecast'][0], 'wind')
    assert content == None
