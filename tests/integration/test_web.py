import pytest
import json
import os
from . import hooks_payloads, repo_payload
import sealedmock
import copy

os.environ["DOTHUB_USER"] = "XXX"
os.environ["DOTHUB_TOKEN"] = "XXX"
import dothub.web

GITHUB_URL = "/github"


def get_mock_response(url):
    """Using the urls in GET_REQUESTS builds a mock and returns it"""
    res_payload = repo_payload.GET_REQUESTS[url]
    mock = sealedmock.SealedMock()
    mock.json.return_value = copy.deepcopy(res_payload)
    mock.raise_for_status = lambda: None
    mock.sealed = True
    return mock


@pytest.fixture()
def app():
    return dothub.web.app.test_client()


@pytest.fixture()
def trigger_hook(app):
    def _(event, payload):
        response = app.post(
            GITHUB_URL,
            data=json.dumps(payload),
            headers={'X-GitHub-Event': event},
            content_type='application/json'
        )
        response.json = json.loads(response.data.decode("utf-8"))
        return response
    return _


def test_index_get_succeeds(app):
    response = app.get('/')
    assert response.status_code == 200


def test_only_post_accepted_on_github(app):
    assert 405 == app.get(GITHUB_URL).status_code
    assert 405 == app.put(GITHUB_URL).status_code
    assert 405 == app.patch(GITHUB_URL).status_code
    assert 405 == app.delete(GITHUB_URL).status_code


def test_post_contains_meta_fields_in_response(trigger_hook):
    response = trigger_hook('unknown', hooks_payloads.PUSH)
    assert 200 == response.status_code
    assert response.json["success"] is True
    assert [] == response.json["actions"]
    assert "baxterthehacker/public-repo" == response.json["repo"]


@sealedmock.patch("dothub.web.GH_HELPER._session")
def test_push_triggers_dothub_sync(session, trigger_hook):
    session.get.side_effect = get_mock_response
    session.patch.return_value.raise_for_status.return_value = None
    session.patch.return_value.text = None
    session.sealed = True
    response = trigger_hook('push', hooks_payloads.PUSH)
    assert 200 == response.status_code
    assert ["repo_sync"] == response.json["actions"]
    session.patch.assert_called_once()
