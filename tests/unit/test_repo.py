"""Unit test for the repository module

It tests the module in isolation from its interface passing a mock
instead of interacting with github
"""
import pytest
import copy
from dothub.repository import Repo
from dothub.github_helper import GitHub
from sealedmock import SealedMock


class GithubData(object):
    repo_config = dict(private=False, has_wiki=True,
                       description='Synchronise your github repositories locally!',
                       homepage='https://pypi.python.org/pypi/hubsync/', has_issues=True,
                       has_downloads=True, name='hubsync')

    collaborators = [
        dict(login='Mariocj89', permissions={'admin': True, 'push': True, 'pull': True})
    ]

    labels = [dict(color='fc2929', name='bug'), dict(color='84b6eb', name='enhancement')]

    hooks = [dict(
        id=1234,
        config=dict(abc=1, bcd=2),
        name='travis',
        active=True,
        events=['pull_request', 'push', 'repository']
    )]


class SerializedData(object):
    options = dict(private=False, has_wiki=True,
                   description='Synchronise your github repositories locally!',
                   homepage='https://pypi.python.org/pypi/hubsync/', has_issues=True,
                   has_downloads=True, name='hubsync')

    collaborators = dict(
        Mariocj89=dict(permission='admin')
    )

    labels = dict(bug=dict(color='fc2929'), enhancement=dict(color='84b6eb'))

    hooks = dict(
        travis=dict(
            id=1234,
            config=dict(abc=1, bcd=2),
            active=True,
            events=['pull_request', 'push', 'repository']
        )
    )


@pytest.mark.parametrize("attribute, response, expected", [
    ("options", GithubData.repo_config, SerializedData.options),
    ("collaborators", GithubData.collaborators, SerializedData.collaborators),
    ("labels", GithubData.labels, SerializedData.labels),
    ("hooks", GithubData.hooks, SerializedData.hooks),
])
def test_get_repo_config(attribute, response, expected):
    gh = SealedMock(GitHub)
    repo = Repo(gh, "owner_name", "repo_name")
    gh.get.return_value = copy.deepcopy(response)
    gh.sealed = True

    result = getattr(repo, attribute)

    assert expected == result


def test_hooks_cannot_update_config_with_tokens():
    gh = SealedMock(GitHub)
    repo = Repo(gh, "owner_name", "repo_name")
    hooks_data = copy.deepcopy(GithubData.hooks)
    hooks_data[0]["config"]["token"] = "*****"
    gh.get.side_effect = lambda *_: copy.deepcopy(hooks_data)
    gh.sealed = True
    hooks_expected = copy.deepcopy(SerializedData.hooks)

    with pytest.raises(RuntimeError):
        repo.hooks = hooks_expected


def test_hooks_can_update_not_config_with_tokens():
    gh = SealedMock(GitHub)
    repo = Repo(gh, "owner_name", "repo_name")
    hooks_data = copy.deepcopy(GithubData.hooks)
    hooks_data[0]["active"] = False
    gh.get.side_effect = lambda *_: copy.deepcopy(hooks_data)
    gh.sealed = True
    hooks_expected = copy.deepcopy(SerializedData.hooks)

    with pytest.raises(RuntimeError):
        repo.hooks = hooks_expected
