"""Test JSON Cut main functions."""
'''
import jsoncut.core

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


@pytest.mark.skip
def test_cut():
    """Test core.cut()."""
    rootkey = 'results'
    getkeys = 'id, via.source'
    delkeys = 'source.from.name'
    result = jsoncut.core.cut(TEST_DATA, rootkey=rootkey, getkeys=getkeys,
                              delkeys=delkeys)
    assert result == PRUNED_TEST_DATA
'''
