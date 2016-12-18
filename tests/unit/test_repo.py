import pytest
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

    hooks = [dict(name='travis', active=True,
                  config={'domain': 'notify.travis-ci.org', 'token': '********',
                          'user': 'Mariocj89'},
                  events=['pull_request', 'push', 'repository'])]


class SerializedData(object):
    options = dict(private=False, has_wiki=True,
                   description='Synchronise your github repositories locally!',
                   homepage='https://pypi.python.org/pypi/hubsync/', has_issues=True,
                   has_downloads=True, name='hubsync')

    collaborators = [
        dict(login='Mariocj89', permissions={'admin': True, 'push': True, 'pull': True})
    ]

    labels = [dict(color='fc2929', name='bug'), dict(color='84b6eb', name='enhancement')]

    hooks = [dict(name='travis', active=True,
                  config={'domain': 'notify.travis-ci.org', 'token': '********',
                          'user': 'Mariocj89'},
                  events=['pull_request', 'push', 'repository'])]


@pytest.mark.parametrize("attribute, response, expected", [
    ("options", GithubData.repo_config, SerializedData.options),
    ("collaborators", GithubData.collaborators, SerializedData.collaborators),
    ("labels", GithubData.labels, SerializedData.labels),
    ("hooks", GithubData.hooks, SerializedData.hooks),
])
def test_get_repo_config(attribute, response, expected):
    gh = SealedMock(GitHub)
    repo = Repo(gh, "owner_name", "repo_name")
    gh.get.return_value = response
    gh.sealed = True

    result = getattr(repo, attribute)

    assert expected == result
