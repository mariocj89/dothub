"""Tests updating config of a real org and repo under the dothub-sandbox organization

Tests in this file target the real gothub organization of "dothub-sandbox"
Set the environment variable GITHUB_TOKEN (only if any maintainer gave it to you)
 to run these tests
"""

import pytest
from click.testing import CliRunner
import tempfile
from dothub.cli import dothub
from dothub import utils
import os

import logging
logging.basicConfig(level=logging.DEBUG)

DOTHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CLI_BASE_ARGS = [
    "--user=dothub-bot", "--token=" + str(DOTHUB_TOKEN),
    "--verbosity=DEBUG"  # This logs all req/res
]


ORG_CONFIG = {
    'teams': {
        'test-team': {
            'description': 'This is a test team',
            'members': {
                'dothub-bot': {
                    'role': 'maintainer'
                }
            },
            'permission': 'pull',
            'privacy': 'closed',
            'repositories': {}
        }
    },
    'hooks': [{
        'active': True,
        'events': [
            'push'
        ],
        'name': 'web',
        'config': {
            'url': 'https://example.com',
            'insecure_ssl': '0',
            'content_type': 'form',
        }
    }],
    'members': {
        'dothub-bot': {
            'role': 'admin'
        },
        'mariocj89': {
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
    'hooks': [{
        'active': True,
        'config': {'domain': 'notify.travis-ci.org'},
        'events': [
            'create', 'delete', 'issue_comment', 'member', 'membership',
            'public', 'pull_request', 'push', 'repository'
        ],
        'name': 'travis',
    }],
    'collaborators': {
        'mariocj89': {
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
        'has_downloads': True,
        'allow_merge_commit': False,
        'allow_squash_merge': True,
        'allow_rebase_merge': True
    }
}


skip_on_no_token = pytest.mark.skipif(
    not DOTHUB_TOKEN,
    reason="Missing DOTHUB user token for integration tests"
)


@pytest.fixture
def preserve_org():
    """Saves the org config and restores it at the end of each test"""
    if DOTHUB_TOKEN:
        with tempfile.NamedTemporaryFile() as original_config:
            original_config_file = original_config.name

        args = CLI_BASE_ARGS + ["pull", "dothub-sandbox", original_config_file]
        result = CliRunner().invoke(dothub, args, obj={})
        assert 0 == result.exit_code, result.output

        yield

        args = CLI_BASE_ARGS + ["push", "dothub-sandbox", original_config_file]
        result = CliRunner().invoke(dothub, args, obj={})
        assert 0 == result.exit_code, result.output
    else:
        yield


@pytest.fixture
def preserve_repo():
    """Saves the repo config and restores it at the end of each test"""
    if DOTHUB_TOKEN:
        with tempfile.NamedTemporaryFile() as original_config:
            original_config_file = original_config.name

        args = CLI_BASE_ARGS + ["pull", "dothub-sandbox/test-repo", original_config_file]
        result = CliRunner().invoke(dothub, args, obj={})
        assert 0 == result.exit_code, result.output

        yield

        args = CLI_BASE_ARGS + ["push", "dothub-sandbox/test-repo", original_config_file]
        result = CliRunner().invoke(dothub, args, obj={})
        assert 0 == result.exit_code, result.output
    else:
        yield


@skip_on_no_token
def test_update_org_configuration(preserve_org):
    """Update dothub-sandbox organization

    Updates the repo by setting the configuration as stated in ORG_CONFIG
    The preserve_org fixture ensure that the org is left as it was after running the test
    """
    runner = CliRunner()
    with tempfile.NamedTemporaryFile() as test_config:
        test_config_file = test_config.name

    # ########################
    # Test updating the config
    # ########################
    utils.serialize_yaml(ORG_CONFIG, test_config_file)
    args = CLI_BASE_ARGS + ["push", "dothub-sandbox", test_config_file]
    result = runner.invoke(dothub, args, obj={})
    assert 0 == result.exit_code, result.output

    # ##########################
    # Test retrieving the config
    # ##########################
    args = CLI_BASE_ARGS + ["pull", "dothub-sandbox", test_config_file]
    result = runner.invoke(dothub, args, obj={})
    assert 0 == result.exit_code, result.output
    assert ORG_CONFIG == utils.load_yaml(test_config_file)


@skip_on_no_token
def test_update_repo_configuration(preserve_repo):
    """Update dothub-sandbox/test-repo repository

    Updates the repo by setting the configuration as stated in REPO_CONFIG
    The preserve_repo fixture ensures that the repo is left as it was after running the test
    """
    runner = CliRunner()
    with tempfile.NamedTemporaryFile() as test_config:
        test_config_file = test_config.name

    # ########################
    # Test updating the config
    # ########################
    utils.serialize_yaml(REPO_CONFIG, test_config_file)
    args = CLI_BASE_ARGS + ["push", "dothub-sandbox/test-repo", test_config_file]
    result = runner.invoke(dothub, args, obj={})
    assert 0 == result.exit_code, result.output

    # ##########################
    # Test retrieving the config
    # ##########################
    args = CLI_BASE_ARGS + ["pull", "dothub-sandbox/test-repo", test_config_file]
    result = runner.invoke(dothub, args, obj={})
    assert 0 == result.exit_code, result.output
    assert REPO_CONFIG == utils.load_yaml(test_config_file)

