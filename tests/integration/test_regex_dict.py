from .regex_dict import RegExDict


def test_regex_dict():
    d = RegExDict()
    d["I .* coke"] = 5
    d["You .* coke"] = 0

    assert d["I love coke"] == 5
    assert d["You hate coke"] == 0

    assert d.get("I hate coke") == 5
    assert d.get("All of us hate coke") is None
    assert d.get("All of us hate coke", 1) == 1
