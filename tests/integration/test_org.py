"""Integration tests for organization control"""
from .regex_dict import RegExDict
from click.testing import CliRunner
from dothub._main import dothub
from dothub import utils
import copy
import yaml
import tempfile
import sealedmock
import mock
from . import data_utils


GET_REQUESTS = RegExDict(data_utils.REPO_AND_ORG_DATA)

base_args = ["--user=xxx", "--token=yyy"]


EXPECTED_RESULT = """hooks: {}
members:
  Mariocj89:
    role: admin
  dnaranjo89:
    role: admin
  palvarez89:
    role: admin
options:
  billing_email: mariocj89@gmail.com
  company: null
  description: Group of friends that code :)
  email: ''
  location: ''
  name: EtCaterva
teams:
  Automation:
    description: ''
    id: 1338338
    members:
      Mariocj89:
        role: member
      palvarez89:
        role: member
    permission: admin
    privacy: closed
    repositories:
      deployment:
        permission: push
  Mobile:
    description: Pepole working in the apps
    id: 1827619
    members:
      Mariocj89:
        role: member
    permission: pull
    privacy: closed
    repositories:
      deployment:
        permission: pull
      echaloasuerte-mobile:
        permission: pull
  Web:
    description: Web developers
    id: 1827620
    members:
      Mariocj89:
        role: member
      dnaranjo89:
        role: member
    permission: pull
    privacy: closed
    repositories:
      echaloasuerte:
        permission: push
      echaloasuerte-legacy:
        permission: push
      etcaterva-web:
        permission: push
"""


SAMPLE_REPO_CONFIG = {
    'collaborators': {
        'Mariocj89': {
            'permission': 'admin'
        }
    },
    'hooks': {
        'travis': {
            'active': False,
            'config': {
                'domain': 'notify.travis-ci.org',
                'token': '********',
                'user': 'Mariocj89'
            },
            'events': ['issue_comment', 'member', 'public', 'pull_request', 'push']
        }
    },
    'labels': {
        'bug': {'color': 'fc2929'},
        'duplicate': {'color': 'cccccc'},
        'enhancement': {'color': '84b6eb'},
        'help wanted': {'color': '159818'},
        'invalid': {'color': 'e6e6e6'},
        'question': {'color': 'cc317c'},
        'wontfix': {'color': 'ffffff'}
    },
    'options': {
        'has_downloads': True,
        'has_issues': False,
        'has_wiki': True,
        'private': False,
        'name': "THIS IS IGNORED!!!!"
    }
}


def get_mock_response(url):
    """Using the urls in GET_REQUESTS builds a mock and returns it"""
    res_payload = GET_REQUESTS[url]
    mock = sealedmock.SealedMock()
    mock.json.return_value = copy.deepcopy(res_payload)
    mock.raise_for_status = lambda: None
    mock.sealed = True
    return mock


@sealedmock.patch("dothub._main.github_helper.requests.Session")
def test_repo_serialization(session_mock):
    runner = CliRunner()
    session_mock.return_value.get.side_effect = get_mock_response
    session_mock.sealed = True
    with tempfile.NamedTemporaryFile() as file_:
        args = base_args + ["org", "--name=etcaterva", "pull",
                            "--output_file=" + file_.name]
        result = runner.invoke(dothub, args, obj={})

        assert 0 == result.exit_code
        with open(file_.name) as f:
            result_config = f.read()
        assert EXPECTED_RESULT == result_config


@sealedmock.patch("dothub._main.github_helper.requests.Session")
def test_org_push_without_changes(session_mock):
    runner = CliRunner()
    session_mock.return_value.get.side_effect = get_mock_response
    session_mock.sealed = True
    with tempfile.NamedTemporaryFile() as file_:
        with open(file_.name, 'w') as f:
            f.write(EXPECTED_RESULT)

        args = base_args + ["org", "--name=etcaterva", "push",
                            "--input_file=" + file_.name]
        result = runner.invoke(dothub, args, obj={})

        assert 0 == result.exit_code
        # session put/patch/delete were not called


@sealedmock.patch("dothub._main.github_helper.requests.Session")
def test_repo_push_with_changes(session_mock):
    runner = CliRunner()
    session_mock.return_value.get.side_effect = get_mock_response
    session_mock.return_value.post.return_value = mock.MagicMock()
    session_mock.return_value.patch.return_value = mock.MagicMock()
    session_mock.return_value.put.return_value = mock.MagicMock()
    session_mock.return_value.delete.return_value = mock.MagicMock()
    session_mock.sealed = True

    new_config = yaml.safe_load(EXPECTED_RESULT)
    # Remove a member
    member_config = new_config['members'].pop("palvarez89")
    # Add member
    new_config['members']["new_member"] = member_config
    # Updated member
    new_config['members']["Mariocj89"]["role"] = "member"

    new_config["options"]["company"] = "Bloomberg"

    team_config = new_config["teams"].pop("Automation")
    new_config["teams"]["new_team"] = team_config

    with tempfile.NamedTemporaryFile() as file_:
        with open(file_.name, 'w') as f:
            yaml.safe_dump(new_config, f, encoding='utf-8', allow_unicode=True,
                           default_flow_style=False)

        args = base_args + ["org", "--name=etcaterva", "push",
                            "--input_file=" + file_.name]
        result = runner.invoke(dothub, args, obj={})

    assert 0 == result.exit_code
    assert 1 == session_mock.return_value.post.call_count
    assert 5 == session_mock.return_value.put.call_count
    assert 2 == session_mock.return_value.delete.call_count
    assert 1 == session_mock.return_value.patch.call_count


@sealedmock.patch("dothub._main.github_helper.requests.Session")
def test_org_push_all_repos_without_changes(session_mock):
    runner = CliRunner()
    session_mock.return_value.get.side_effect = get_mock_response
    session_mock.sealed = True
    with tempfile.NamedTemporaryFile() as file_:
        utils.serialize_yaml(SAMPLE_REPO_CONFIG, file_.name)
        args = base_args + ["org", "--name=etcaterva", "repos",
                            "--input_file=" + file_.name]
        result = runner.invoke(dothub, args, obj={})

        assert 0 == result.exit_code
        # session put/patch/delete were not called

    repo_url = "https://api.github.com/repos/etcaterva/echaloasuerte"
    session_mock.return_value.get.assert_any_call(repo_url)
