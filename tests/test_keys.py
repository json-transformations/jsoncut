from jsoncut.core import cut
from jsoncut.tokenizer import parse_key_name
from jsoncut.treecrawler import find_keys
from .sample_data import keys_with_dots

TEST_DATA_WITH_DOTS_IN_KEY_NAME = {"dots.in.key.name": {"k1": True}}


def test_list_key_name_containing_dots():
    result = list(find_keys(TEST_DATA_WITH_DOTS_IN_KEY_NAME))
    assert result == ['dots\\.in\\.key\\.name', 'dots\\.in\\.key\\.name.k1']


def test_parse_key_name_containing_dots():
    keys = find_keys(TEST_DATA_WITH_DOTS_IN_KEY_NAME)
    result = parse_key_name(keys[0])
    assert result == ('dots.in.key.name',)

    result = parse_key_name(keys[1])
    assert result == ('dots.in.key.name', 'k1')


def test_cut_key_number_containing_dots_in_name():
    result = cut(keys_with_dots.TEST_DATA, getkeys='4')
    assert result == [{'Name': 'running'}, {'Name': 'running'}]


def test_cut_key_number_containing_dots_in_name_with_fullpath():
    result = cut(keys_with_dots.TEST_DATA, getkeys='4', fullpath=True)
    assert result == [{'State.Name': 'running'}, {'State.Name': 'running'}]
