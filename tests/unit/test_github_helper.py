"""Validates functionality on the github_helper module

Tests in this file are independent of environment and rely on nothing else but the
code under test in github_helper.py

To mock out the HTTP requests being sent `requests_mock` is used
"""
import pytest
import requests_mock
import os.path

from dothub.github_helper import GitHub, DEFAULT_API_URL


# #######
# HELPERS
# #######

def register_uri(mock, method, url, base_url=DEFAULT_API_URL, **kwargs):
    absolute_url = os.path.join(base_url, url)
    mock.register_uri(method, absolute_url, **kwargs)


# ########
# FIXTURES
# ########

@pytest.fixture
def gh():
    """Gives an instance of github helper"""
    return GitHub(user="User", token="TOKEN")


# ##########
# TEST CASES
# ##########

def test_create_github_helper(gh):
    """Create an instance of github_helper"""
    assert gh is not None


def test_get_returns_unexpected_type(gh):
    """When an unexpected type is returned on get, raises"""
    target_url = "url"
    with requests_mock.Mocker() as mock:
        register_uri(mock, "GET", target_url, text="TEXT")
        with pytest.raises(ValueError):
            gh.get(target_url, fields=[])


def test_get_returns_payload(gh):
    """A get requests returns content on json payload"""
    target_url = "url"
    with requests_mock.Mocker() as mock:
        register_uri(mock, "GET", target_url, json=dict(
            key1="a",
            key2=1,
            key3=2,
        ))
        result = gh.get(target_url, fields=["key1", "key2"])
        assert result is not None


def test_get_returns_dictionary_with_keys_in_fields(gh):
    """A get requests returns just the fields in the fields list"""
    target_url = "url"
    with requests_mock.Mocker() as mock:
        register_uri(mock, "GET", target_url, json=dict(
            key1="a",
            key2=1,
            key3=2,
        ))
        result = gh.get(target_url, fields=["key1", "key2"])
        assert result["key1"] == "a"
        assert result["key2"] == 1
        assert "key3" not in result


def test_get_fields_can_be_wider_than_the_actual(gh):
    """The list in the fields parameter can be wider than the keys"""
    target_url = "url"
    with requests_mock.Mocker() as mock:
        register_uri(mock, "GET", target_url, json=dict(
            key1="a",
        ))
        result = gh.get(target_url, fields=["key1", "key2"])
        assert result["key1"] == "a"
        assert "key2" not in result


def test_get_returns_list_filters_keys_on_each_dict(gh):
    """Fields are filtered for each item in the list"""
    target_url = "url"
    with requests_mock.Mocker() as mock:
        register_uri(mock, "GET", target_url, json=[
            dict(key1=1, key3=3),
            dict(key2=2, key3=3),
        ])
        result = gh.get(target_url, fields=["key1", "key2"])
        assert all("key3" not in d for d in result)
        assert any("key1" in d for d in result)
        assert any("key2" in d for d in result)


def test_put_success(gh):
    """Put requests are sent successfully"""
    target_url = "url"
    with requests_mock.Mocker() as mock:
        register_uri(mock, "PUT", target_url, json={})
        result = gh.put(target_url, {})
        assert result == {}


def test_post_without_response(gh):
    """Post request without response yield no response"""
    target_url = "url"
    with requests_mock.Mocker() as mock:
        register_uri(mock, "POST", target_url, text=None)
        result = gh.post(target_url, dict(k=1))
        assert result is None


def test_post_success(gh):
    """Post requests are sent successfully"""
    target_url = "url"
    with requests_mock.Mocker() as mock:
        register_uri(mock, "POST", target_url, json={})
        result = gh.post(target_url, dict(k=1))
        assert result == {}


def test_delete_success(gh):
    """Delete requests are sent successfully"""
    target_url = "url"
    with requests_mock.Mocker() as mock:
        register_uri(mock, "DELETE", target_url, text=None)
        result = gh.delete(target_url)
        assert result is None


def test_use_different_base_url():
    """Building the github helper with a different url, propagates to requests"""
    gh = GitHub(user="User", token="TOKEN", api_url="http://NEW_BASE")
    target_url = "url"
    with requests_mock.Mocker() as mock:
        register_uri(mock, "GET", target_url, base_url="http://NEW_BASE", json=dict(
            key1="a",
            key2=1,
            key3=2,
        ))
        result = gh.get(target_url, fields=["key1", "key2"])
        assert result is not None


