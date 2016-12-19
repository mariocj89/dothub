"""Helper to diff dicts"""
from collections import namedtuple


DiffDict = namedtuple("DiffDict", "added missing updated")


def diff(current_dict, past_dict):
    """Diffs two dicts, the result object has added, missing and updated values"""
    current_dict, past_dict = current_dict, past_dict
    set_current, set_past = set(current_dict.keys()), set(past_dict.keys())
    intersect = set_current.intersection(set_past)
    updated = set(o for o in intersect if past_dict[o] != current_dict[o])

    return DiffDict(set_past - intersect, set_current - intersect, updated)
