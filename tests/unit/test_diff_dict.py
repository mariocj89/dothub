from dothub import dict_diff


def test_diff_empty_dicts():
    dict_a = dict()
    dict_b = dict()

    added, missing, updated = dict_diff.diff(dict_a, dict_b)

    assert added == set()
    assert missing == set()
    assert updated == set()


def test_equal_dicts():
    dict_a = dict(a=1, b="b", c=[1, 2])
    dict_b = dict(a=1, b="b", c=[1, 2])

    added, missing, updated = dict_diff.diff(dict_a, dict_b)

    assert added == set()
    assert missing == set()
    assert updated == set()


def test_full_diff_dicts():
    dict_a = dict(b="b", c=[1, 2])
    dict_b = dict(a=1, c=[1])

    added, missing, updated = dict_diff.diff(dict_a, dict_b)

    assert added == set('a')
    assert missing == set('b')
    assert updated == set('c')
