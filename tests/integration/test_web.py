import pytest
import json
import os
from . import hooks_payloads
from . import regex_dict
from . import data_utils
import copy
import sealedmock

os.environ["DOTHUB_USER"] = "XXX"
os.environ["DOTHUB_TOKEN"] = "XXX"
import dothub.web

GITHUB_URL = "/github"


REQUESTS_PAYLOAD = regex_dict.RegExDict(data_utils.REPO_AND_ORG_DATA)


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


@sealedmock.patch("dothub.web.GH_HELPER._session")
def test_post_contains_meta_fields_in_response(session, trigger_hook):
    session.get.side_effect = data_utils.requests_mock(
        regex_dict.RegExDict(data_utils.REPO_AND_ORG_DATA)
    )
    response = trigger_hook('unknown', hooks_payloads.PUSH)
    assert 200 == response.status_code
    assert response.json["success"] is True
    assert [] == response.json["actions"]
    assert "etcaterva/echaloasuerte" == response.json["repo"]


@sealedmock.patch("dothub.web.GH_HELPER._session")
def test_push_triggers_no_change(session, trigger_hook):
    session.get.side_effect = data_utils.requests_mock(
        regex_dict.RegExDict(data_utils.REPO_AND_ORG_DATA)
    )
    session.sealed = True
    response = trigger_hook('push', hooks_payloads.PUSH)
    assert 200 == response.status_code
    assert not response.json["actions"]


@sealedmock.patch("dothub.web.GH_HELPER._session")
def test_push_triggers_repo_update(session, trigger_hook):
    payloads = regex_dict.RegExDict(copy.deepcopy(data_utils.REPO_AND_ORG_DATA))
    payloads["/repos/etcaterva/echaloasuerte"]["description"] = "New description"
    session.get.side_effect = data_utils.requests_mock(payloads)
    session.patch.return_value.raise_for_status.return_value = None
    session.patch.return_value.text = None
    session.sealed = True
    response = trigger_hook('push', hooks_payloads.PUSH)
    assert 200 == response.status_code
    assert "repo_update" in response.json["actions"]
    session.patch.assert_called_once()


@sealedmock.patch("dothub.web.GH_HELPER._session")
def test_push_triggers_org_update(session, trigger_hook):
    payloads = regex_dict.RegExDict(copy.deepcopy(data_utils.REPO_AND_ORG_DATA))
    payloads["/orgs/etcaterva"]["description"] = "New description"
    session.get.side_effect = data_utils.requests_mock(payloads)
    session.patch.return_value.raise_for_status.return_value = None
    session.patch.return_value.text = None
    session.sealed = True
    response = trigger_hook('push', hooks_payloads.PUSH)
    assert 200 == response.status_code
    assert "org_update" in response.json["actions"]
    session.patch.assert_called_once()


@sealedmock.patch("dothub.web.GH_HELPER._session")
def test_non_push_triggers_repo_sync(session, trigger_hook):
    payloads = regex_dict.RegExDict(copy.deepcopy(data_utils.REPO_AND_ORG_DATA))
    payloads["/repos/etcaterva/echaloasuerte"]["description"] = "New description"
    session.get.side_effect = data_utils.requests_mock(payloads)
    session.patch.return_value.raise_for_status.return_value = None
    session.patch.return_value.text = None
    session.sealed = True
    response = trigger_hook('other_action', hooks_payloads.PUSH)
    assert 200 == response.status_code
    assert "repo_sync" in response.json["actions"]
    session.patch.assert_called_once()


@sealedmock.patch("dothub.web.GH_HELPER._session")
def test_non_push_triggers_org_sync(session, trigger_hook):
    payloads = regex_dict.RegExDict(copy.deepcopy(data_utils.REPO_AND_ORG_DATA))
    payloads["/orgs/etcaterva"]["description"] = "New description"
    session.get.side_effect = data_utils.requests_mock(payloads)
    session.patch.return_value.raise_for_status.return_value = None
    session.patch.return_value.text = None
    session.sealed = True
    response = trigger_hook('other_action', hooks_payloads.PUSH)
    assert 200 == response.status_code
    assert "org_sync" in response.json["actions"]
    session.patch.assert_called_once()
