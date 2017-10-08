"""Validates functionality of the repository objects

Unit-tests in this file rely on the code within github_helper to test the repository.py
code. The code for github_helper is validated in a different test suite and therefore
considered safe to test repository.py.

It has been decided to rely on the code in github_helpers as this abstraction is more
likely to change than the API of github itself. Therefore all mocking is performed
at requests level by using requests_mock.
"""

import pytest
import requests_mock
import os.path
from mock import Mock, ANY
from copy import deepcopy

from dothub import github_helper
from dothub.repository import Repo, FIELDS


# ################
# GLOBAL CONSTANTS
# ################

REPO_OWNER = "OWNER"
REPO_NAME = "NAME"


# #######
# HELPERS
# #######

def register_uri(mock, method, url, **kwargs):
    """Registers an url on requests_mock ensure the full url was passed"""
    absolute_url = os.path.join(github_helper.DEFAULT_API_URL, url)
    mock.register_uri(method, absolute_url, **kwargs)


def add_repo_options(mock, value):
    """Add options for a repository"""
    url = os.path.join("repos", REPO_OWNER, REPO_NAME)
    register_uri(mock, "GET", url=url, json=value)


def allow_repo_method(mock, method, url_extra=None):
    """Allow a specific method to be run against the base repo url

    Allow a method to be applied on a url within the repo.
    Ex: to allow patch on /repos/owner/name/labels/label1
     call allow_repo_method(mock, "PATCH", "labels/label1")
    """
    url = os.path.join("repos", REPO_OWNER, REPO_NAME)
    if url_extra:
        url = os.path.join(url, url_extra)
    register_uri(mock, method, url=url)


def add_repo_labels(mock, values):
    """Add labels for a repository"""
    url = os.path.join("repos", REPO_OWNER, REPO_NAME, "labels")
    register_uri(mock, "GET", url=url, json=values)


def add_repo_collaborators(mock, values):
    """Add collaborators for a repository"""
    url = os.path.join("repos", REPO_OWNER, REPO_NAME, "collaborators")
    register_uri(mock, "GET", url=url, json=values)


def add_repo_hooks(mock, values):
    """Add hooks for a repository"""
    url = os.path.join("repos", REPO_OWNER, REPO_NAME, "hooks")
    register_uri(mock, "GET", url=url, json=values)


# ####
# DATA
# ####

class DF(object):
    """Data factory

    Just creates data. :)
    Not using constants or factory to ensure a fresh copy is generated on each call
    """
    @staticmethod
    def options():
        return dict(
            name="the_name",
            description="Sample description goes here",
            homepage="http://homepage.org",
            private=False,
            has_issues=True,
            has_wiki=True,
            has_downloads=False,
            allow_rebase_merge=True,
            allow_squash_merge=False,
            allow_merge_commit=False,
        )

    @staticmethod
    def labels():
        return [
            dict(
                id=1,
                name="label1",
                color="f29513",
                default=True,
            ),
            dict(
                id=2,
                name="label2",
                color="0f11f0",
                default=False,
            ),
        ]

    @staticmethod
    def collaborators():
        return [
            dict(
                login="collaborator1",
                permissions=dict(
                    pull=True,
                    push=False,
                    admin=False
                )
            ),
            dict(
                login="collaborator2",
                permissions=dict(
                    pull=True,
                    push=True,
                    admin=False
                )
            ),
            dict(
                login="collaborator3",
                permissions=dict(
                    pull=True,
                    push=True,
                    admin=True
                )
            ),
        ]

    @staticmethod
    def hooks():
        return [
            dict(
                id=1,
                name="hook1",
                active=True,
                events=[
                    "push",
                    "pull_request",
                ],
                config=dict(
                    url="http://content",
                    content="json",
                    custom_param="custom",
                )
            ),
            dict(
                id=2,
                name="web",
                active=False,
                events=[
                    "push",
                ],
                config=dict(
                    token="******",
                    url="https://chooserandom.com/webhook",
                )
            ),
        ]


# ########
# FIXTURES
# ########

@pytest.fixture
def gh():
    """Gives an instance of github helper"""
    return github_helper.GitHub(user="User", token="TOKEN")


@pytest.fixture
def repo(gh):
    """Creates a Repo instance and adds an spy attribute to check for calls"""
    ret = Repo(gh, owner=REPO_OWNER, repository=REPO_NAME)
    ret._gh = Mock(wraps=ret._gh)
    ret.spy = ret._gh
    return ret


# ##########
# TEST CASES
# ##########

def test_create_repository(repo):
    """Create an instance of repository"""
    assert repo is not None


def test_get_repo_options(repo):
    """Retrieving the basic repo options"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        assert repo.options["name"] == "the_name"
        assert repo.options == DF.options()


def test_get_untracked_features_wont_appear(repo):
    """Retrieving the basic repo options only show the listed features"""
    with requests_mock.Mocker() as mock:
        options = DF.options()
        options["future_feature"] = "Yeah!"
        add_repo_options(mock, options)
        assert set(FIELDS["repo"]["options"]) == set(repo.options)
        assert "future_feature" not in repo.options


def test_set_options_unchanged_sends_no_request(repo):
    """Updating the repo options with no changes is no-op"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        repo.options = DF.options()


def test_set_options_sends_patch(repo):
    """Updating the repo options with no changes is no-op"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        allow_repo_method(mock, "PATCH")
        options = DF.options()
        options["description"] = "Yeah!"
        repo.options = options
        repo.spy.patch.assert_called_once()


def test_get_labels(repo):
    """Retrieve multiple labels via the repository method"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_labels(mock, DF.labels())
        assert repo.labels == {
            "label1": dict(
                color="f29513",
            ),
            "label2": dict(
                color="0f11f0",
            ),
        }


def test_get_labels_no_results(repo):
    """Retrieve labels from repo without labels gives empty dict"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_labels(mock, [])
        assert repo.labels == {}


def test_set_labels_unchanged(repo):
    """No change on labels -> no request sent"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_labels(mock, DF.labels())

        repo.labels = {
            "label1": dict(
                color="f29513",
            ),
            "label2": dict(
                color="0f11f0",
            ),
        }


def test_set_labels_add_one(repo):
    """Add a single label calls post"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_labels(mock, DF.labels())
        allow_repo_method(mock, "POST", url_extra="labels")

        repo.labels = {
            "label1": dict(
                color="f29513",
            ),
            "label2": dict(
                color="0f11f0",
            ),
            "label3": dict(
                color="000000",
            ),
        }
        repo.spy.post.assert_called_once_with(ANY, dict(
            name="label3",
            color="000000",
        ))


def test_set_labels_delete_one(repo):
    """Delete a single label calls delete"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_labels(mock, DF.labels())
        allow_repo_method(mock, "DELETE", url_extra="labels/label2")

        repo.labels = {
            "label1": dict(
                color="f29513",
            ),
        }
        repo.spy.delete.assert_called_once()


def test_set_labels_update_color(repo):
    """Update the color of a label calls patch on it"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_labels(mock, DF.labels())
        allow_repo_method(mock, "PATCH", url_extra="labels/label2")

        repo.labels = {
            "label1": dict(
                color="f29513",
            ),
            "label2": dict(
                color="ffffff",
            ),
        }
        repo.spy.patch.assert_called_once_with(ANY, dict(
            name="label2",
            color="ffffff",
        ))


@pytest.mark.xfail(reason="Label renaming not implemented", run=False)
def test_set_labels_rename(repo):
    """Renaming a label patches it

    Marked as failed as at the moment it is just recreating and deleting.
    This is an issue as all issues will be untagged since the id is different.
    """
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_labels(mock, DF.labels())
        allow_repo_method(mock, "PATCH", url_extra="labels/label2")

        repo.labels = {
            "label1": dict(
                color="f29513",
            ),
            "label3": dict(
                color="ffffff",
            ),
        }
        repo.spy.patch.assert_called_once_with(ANY, dict(
            name="label3",
            color="ffffff",
        ))


def test_get_collaborators_multiple_returned(repo):
    """Retrieve multiple collaborators"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_collaborators(mock, DF.collaborators())
        assert repo.collaborators == dict(
            collaborator1=dict(permission="pull"),
            collaborator2=dict(permission="push"),
            collaborator3=dict(permission="admin"),
        )


def test_set_collaborators_unchanged(repo):
    """No change on colaborators -> no request sent"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_collaborators(mock, DF.collaborators())

        repo.collaborators = dict(
            collaborator1=dict(
                permission="pull",
            ),
            collaborator2=dict(
                permission="push",
            ),
            collaborator3=dict(
                permission="admin",
            ),
        )


def test_set_collaborators_add_one(repo):
    """Add a single collaborator calls post"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_collaborators(mock, DF.collaborators())
        allow_repo_method(mock, "PUT", url_extra="collaborators/collaborator4")

        repo.collaborators = dict(
            collaborator1=dict(
                permission="pull",
            ),
            collaborator2=dict(
                permission="push",
            ),
            collaborator3=dict(
                permission="admin",
            ),
            collaborator4=dict(
                permission="push",
            ),
        )
        repo.spy.put.assert_called_once_with(ANY, dict(permission="push"))


def test_set_collaborators_delete_one(repo):
    """Delete a single collaborator calls delete"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_collaborators(mock, DF.collaborators())
        allow_repo_method(mock, "DELETE", url_extra="collaborators/collaborator3")

        repo.collaborators = dict(
            collaborator1=dict(
                permission="pull",
            ),
            collaborator2=dict(
                permission="push",
            ),
        )
        repo.spy.delete.assert_called_once()


def test_set_collaborators_update_permission(repo):
    """Update the permission of a collaborator deletes and put

    At the time of writing this implementation there is no way to update the permissions
    therefore the update is implemented by removing the user from the repository and
    adding it again
    """
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_collaborators(mock, DF.collaborators())
        allow_repo_method(mock, "DELETE", url_extra="collaborators/collaborator1")
        allow_repo_method(mock, "PUT", url_extra="collaborators/collaborator1")

        repo.collaborators = dict(
            collaborator1=dict(
                permission="admin",
            ),
            collaborator2=dict(
                permission="push",
            ),
            collaborator3=dict(
                permission="admin",
            ),
        )
        repo.spy.delete.assert_called_once()
        repo.spy.put.assert_called_once_with(ANY, dict(
            permission="admin"
        ))


def test_get_hooks_multiple_returned(repo):
    """Retrieve multiple hooks"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_hooks(mock, DF.hooks())
        assert repo.hooks == [
            dict(
                name="hook1",
                active=True,
                events=[
                    "push",
                    "pull_request",
                ],
                config=dict(
                    url="http://content",
                    content="json",
                    custom_param="custom",
                )
            ),
            dict(
                name="web",
                active=False,
                events=[
                    "push",
                ],
                config=dict(
                    token="******",
                    url='https://chooserandom.com/webhook',
                )
            )
        ]


def test_set_hook_add_one(repo):
    """Adding a hook calls post"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_hooks(mock, DF.hooks())
        allow_repo_method(mock, "POST", url_extra="hooks")
        repo.hooks = [
            dict(
                name="hook1",
                active=True,
                events=[
                    "push",
                    "pull_request",
                ],
                config=dict(
                    url="http://content",
                    content="json",
                    custom_param="custom",
                )
            ),
            dict(
                active=False,
                name="web",
                events=[
                    "push",
                ],
                config=dict(
                    token="******",
                    url="https://chooserandom.com/webhook",
                )
            ),
            dict(
                name="web",
                active=True,
                events=[
                    "push",
                ],
                config=dict(
                    url="https://chooserandom2.com/webhook",
                )
            ),
        ]
        repo.spy.post.assert_called_once_with(ANY, dict(
            name="web",
            active=True,
            events=["push"],
            config=dict(url="https://chooserandom2.com/webhook")
        ))


def test_set_hooks_unchanged(repo):
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_hooks(mock, DF.hooks())
        same_hooks = DF.hooks()
        for h in same_hooks:
            h.pop('id')
        repo.hooks = same_hooks


def test_set_hook_remove_one(repo):
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_hooks(mock, DF.hooks())
        hooks = DF.hooks()
        deleted = hooks.pop()
        for h in hooks:
            h.pop('id')
        allow_repo_method(mock, "DELETE", url_extra="hooks/{}".format(deleted["id"]))

        repo.hooks = hooks


def test_set_hook_update_one(repo):
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_hooks(mock, DF.hooks())
        hooks = DF.hooks()
        updated = hooks[0]
        allow_repo_method(mock, "PATCH", url_extra="hooks/{}".format(updated["id"]))
        for h in hooks:
            h.pop('id')
        updated["active"] = not updated["active"]

        repo.hooks = hooks


def test_set_hook_invalid_update_in_config(repo):
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_hooks(mock, DF.hooks())
        hooks = DF.hooks()
        updated = hooks[0]
        updated["config"]["token"] = "secret_password"
        allow_repo_method(mock, "PATCH", url_extra="hooks/{}".format(updated["id"]))
        for h in hooks:
            h.pop('id')
        updated["active"] = not updated["active"]

        with pytest.raises(RuntimeError) as exc:
            repo.hooks = hooks
            assert "secrets is not supported" in str(exc)


def test_describe_full_repo(repo):
    """Retrieve all properties of the repo

    This test should detect any change on how the configuration is serialized.

    Even if it seems annoying having to change this test on any change on serialization
    it is a great way to verify any change that might be accidentally done on the
    retrieval of data.
    """
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_labels(mock, DF.labels())
        add_repo_collaborators(mock, DF.collaborators())
        add_repo_hooks(mock, DF.hooks())
        result = repo.describe()
        assert result == {
            'collaborators': {
                'collaborator1': {'permission': 'pull'},
                'collaborator2': {'permission': 'push'},
                'collaborator3': {'permission': 'admin'}
            },
            'hooks': [
                {
                    'name': 'hook1',
                    'active': True,
                    'config': {
                        'content': 'json',
                        'custom_param': 'custom',
                        'url': 'http://content'
                    },
                    'events': ['push', 'pull_request']
                },
                {
                    'name': 'web',
                    'active': False,
                    'config': {
                        'token': '******',
                        'url': 'https://chooserandom.com/webhook',
                    },
                    'events': ['push']
                }
            ],
            'labels': {
                'label1': {'color': 'f29513'},
                'label2': {'color': '0f11f0'}
            },
            'options': {
                'allow_merge_commit': False,
                'allow_rebase_merge': True,
                'allow_squash_merge': False,
                'description': 'Sample description goes here',
                'has_downloads': False,
                'has_issues': True,
                'has_wiki': True,
                'homepage': 'http://homepage.org',
                'name': 'the_name',
                'private': False
            }
        }


def test_update_full_repo_without_changes_triggers_no_request(repo):
    """If the repo is updated with the same configuration, no HTTP requests is sent"""
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_labels(mock, DF.labels())
        add_repo_collaborators(mock, DF.collaborators())
        add_repo_hooks(mock, DF.hooks())
        result = repo.describe()
        repo.update(result)

        # Not really needed as methods not whitelisted, but easier to read :)
        repo.spy.post.assert_not_called()
        repo.spy.patch.assert_not_called()
        repo.spy.put.assert_not_called()


def test_update_full_repo_partial(repo):
    """Update can be passed partial objects

    This test really doesn't verify much other than the function
    does not reject the input
    """
    with requests_mock.Mocker() as mock:
        add_repo_options(mock, DF.options())
        add_repo_labels(mock, DF.labels())
        add_repo_collaborators(mock, DF.collaborators())
        add_repo_hooks(mock, DF.hooks())
        result = repo.describe()
        for part in ['options', 'collaborators', 'hooks', 'labels']:
            temp_data = deepcopy(result)
            temp_data.pop(part)
            repo.update(temp_data)
