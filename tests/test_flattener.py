"""
Test module for the jsoncut.flattener fuctions
"""

import pytest

from jsoncut.flattener import flatten_all
from jsoncut.flattener import flatten_by_keys
from jsoncut.flattener import get_key_content
from jsoncut.exceptions import KeyNotFound

##############################################################################
# SAMPLE DATA
##############################################################################

SOURCE =  {'city': 'jacksonville',
           'data': {'temp': 90,
                    'humidity': 10},
           'info': {'geo': {'lat': 34,
                            'long':-60,
                            },
                    'bordering': ['Georgia',
                                  'Alabama',
                                  'Mississippi',
                                  ],
                    },
            }

FLAT = {'city': 'jacksonville',
        'data.humidity': 10,
        'data.temp': 90,
        'info.bordering': ['Georgia',
                           'Alabama',
                          'Mississippi',
                          ],
        'info.geo.lat': 34,
        'info.geo.long': -60,
        }


##############################################################################
# TESTS flatten_all
##############################################################################

def test_flatten_all():
    """
    GIVEN a json-serialized document
    WHEN the user requests to flatten the entire document
    THEN assert is it flattened and in the correct format
    """
    flattened = flatten_all(SOURCE)
    assert flattened == FLAT


##############################################################################
# TESTS flatten_by_keys
##############################################################################

def test_flatten_by_keys_all():
    """
    GIVEN a json-serialized document
    WHEN the user requests to flatten by does not list keys
    THEN assert it flattens the entire document
    """
    flattened = flatten_by_keys(SOURCE)
    assert flattened == FLAT


def test_flatten_by_keys_KeyNotFound():
    with pytest.raises(KeyNotFound):
        flatten_by_keys(SOURCE, keys=['not.a.real.key'])


##############################################################################
# TESTS get_content
##############################################################################

@pytest.mark.parametrize('key',
    ['city',
    'data.humidity',
    'data.temp',
    'info.bordering',
    'info.geo.lat',
    'info.geo.long',])
def test_get_content_validKey(key):
    """
    GIVEN a json-serialzed document
    WHEN the user requests to flatten one jsoncut-style key
    THEN assert only that key is returned as a dictionary
    """
    destination = {}
    get_key_content(SOURCE, key, destination)
    assert destination == {key : FLAT[key]}


