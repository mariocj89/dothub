"""Tests updating config of a real org and repo under the dothub-sandbox organization"""

import pytest
from click.testing import CliRunner
import tempfile
from dothub._main import dothub
from dothub import utils
import os

DOTHUB_TOKEN = os.environ.get("DOTHUB_USER_TOKEN")
CLI_BASE_ARGS = ["--user=dothub-user", "--token=" + str(DOTHUB_TOKEN)]


ORG_CONFIG = {
    'teams': {
    },
    'hooks': {
        # TO BE IMPLEMENTED
    },
    'members': {
        'dothub-bot': {
            'role': 'admin'
        },
        'Mariocj89': {
            'role': 'admin'
        }
    },
    'options': {
        'billing_email': 'mariocj89+dothub@gmail.com',
        'description': 'Test updating the description',
        'location': None,
        'company': None,
        'name': 'New name',
        'email': None
    }
}

REPO_CONFIG = {
    'labels': {
        'new draw': {
            'color': 'fbca04'
        },
        'feature': {
            'color': '009800'
        },
        'bug': {
            'color': '000000'
        },
        'urgent': {
            'color': 'e11d21'
        },
        'technical': {
            'color': '0052cc'
        }
    },
    'hooks': {
        # TO BE IMPLEMENTED
    },
    'collaborators': {
        'dnaranjo89': {
            'permission': 'admin'
        },
        'Mariocj89': {
            'permission': 'admin'
        },
        'palvarez89': {
            'permission': 'admin'
        },
        'dothub-bot': {
            'permission': 'admin'
        }
    },
    'options': {
        'homepage': 'https://echaloasuerte.com',
        'private': False,
        'has_wiki': False,
        'description': None,
        'has_issues': True,
        'name': 'test-repo',
        'has_downloads': True
    }
}


skip_on_no_token = pytest.mark.skipif(
    not DOTHUB_TOKEN,
    reason="Missing DOTHUB user token for integration tests"
)


@pytest.yield_fixture()
def preserve_org():
    """Saves the org config and restores it at the end of each test"""
    with tempfile.NamedTemporaryFile() as original_config:
        original_config_file = original_config.name

    args = CLI_BASE_ARGS + ["org", "--name=dothub-sandbox", "pull",
                            "--output_file=" + original_config_file]
    result = CliRunner().invoke(dothub, args, obj={})
    assert 0 == result.exit_code

    yield

    args = CLI_BASE_ARGS + ["org", "--name=dothub-sandbox", "push",
                            "--input_file=" + original_config_file]
    result = CliRunner().invoke(dothub, args, obj={})
    assert 0 == result.exit_code


@skip_on_no_token
def test_configure_org(preserve_org):
    runner = CliRunner()
    with tempfile.NamedTemporaryFile() as test_config:
        test_config_file = test_config.name

    # ########################
    # Test updating the config
    # ########################
    utils.serialize_yaml(ORG_CONFIG, test_config_file)
    args = CLI_BASE_ARGS + ["org", "--name=dothub-sandbox", "push",
                            "--input_file=" + test_config_file]
    result = runner.invoke(dothub, args, obj={})
    assert 0 == result.exit_code

    # ##########################
    # Test retrieving the config
    # ##########################
    args = CLI_BASE_ARGS + ["org", "--name=dothub-sandbox", "pull",
                            "--output_file=" + test_config_file]
    result = runner.invoke(dothub, args, obj={})
    assert 0 == result.exit_code
    assert ORG_CONFIG == utils.load_yaml(test_config_file)


@pytest.yield_fixture()
def preserve_repo():
    """Saves the repo config and restores it at the end of each test"""
    with tempfile.NamedTemporaryFile() as original_config:
        original_config_file = original_config.name

    args = CLI_BASE_ARGS + ["repo", "--organization=dothub-sandbox", "--repository=test-repo",
                            "pull", "--output_file=" + original_config_file]
    result = CliRunner().invoke(dothub, args, obj={})
    assert 0 == result.exit_code

    yield

    args = CLI_BASE_ARGS + ["repo", "--organization=dothub-sandbox", "--repository=test-repo",
                            "push", "--input_file=" + original_config_file]
    result = CliRunner().invoke(dothub, args, obj={})
    assert 0 == result.exit_code


@skip_on_no_token
def test_configure_repo(preserve_repo):
    runner = CliRunner()
    with tempfile.NamedTemporaryFile() as test_config:
        test_config_file = test_config.name

    # ########################
    # Test updating the config
    # ########################
    utils.serialize_yaml(REPO_CONFIG, test_config_file)
    args = CLI_BASE_ARGS + ["repo", "--organization=dothub-sandbox", "--repository=test-repo",
                            "push", "--input_file=" + test_config_file]
    result = runner.invoke(dothub, args, obj={})
    assert 0 == result.exit_code

    # ##########################
    # Test retrieving the config
    # ##########################
    args = CLI_BASE_ARGS + ["repo", "--organization=dothub-sandbox", "--repository=test-repo",
                            "pull", "--output_file=" + test_config_file]
    result = runner.invoke(dothub, args, obj={})
    assert 0 == result.exit_code
    assert REPO_CONFIG == utils.load_yaml(test_config_file)

