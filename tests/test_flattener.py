# -*- coding: utf-8 -*-
"""
Test module for the jsoncut.flattener fuctions
"""

import json

import pytest

from jsoncut.flattener import flatten_all

##############################################################################

BEFORE = {'city': 'jacksonville',
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

AFTER_ALL = {'city': 'jacksonville',
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

def test_flatten_all():
    """
    Test that the entire json-serialized document is flattened using the
    jsoncut list format.
    """
    # GIVEN a json-serialized document
    # WHEN the user requests to flatten the entire document
    flattened = flatten_all(BEFORE)
    # THEN assert is it flattened and in the correct format
    assert flattened == AFTER_ALL
