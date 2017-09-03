"""Validates functionality of the organization objects

Unit-tests in this file rely on the code within github_helper to test the organization.py
code. The code for github_helper is validated in a different test suite and therefore
considered safe to test organization.py.

It has been decided to rely on the code in github_helpers as this abstraction is more
likely to change than the API of github itself. Therefore all mocking is performed
at requests level by using requests_mock.
"""

import pytest
import requests_mock
import os.path
from mock import Mock, ANY

from dothub import github_helper
from dothub.organization import Organization


# ################
# GLOBAL CONSTANTS
# ################

ORG_NAME = "ORG_NAME"


# #######
# HELPERS
# #######

def register_uri(mock, method, url, **kwargs):
    """Registers an url on requests_mock ensure the full url was passed"""
    absolute_url = os.path.join(github_helper.DEFAULT_API_URL, url)
    mock.register_uri(method, absolute_url, **kwargs)


def add_org_options(mock, value):
    """Add options for an organization"""
    url = os.path.join("orgs", ORG_NAME)
    register_uri(mock, "GET", url=url, json=value)


def add_org_members(mock, values):
    """Add members for an organization

    This method fills two end points. Members and memberships

    The values passed is an array of dictionaries with login as key and the value
    will be used to fill an entry on the membership endpoint
    """
    url = os.path.join("orgs", ORG_NAME, "members")
    members_response = [dict(login=member) for member in values]
    register_uri(mock, "GET", url=url, json=members_response)
    for name, membership in values.items():
        ms_url = os.path.join("orgs", ORG_NAME, "memberships", name)
        register_uri(mock, "GET", url=ms_url, json=membership)


def add_org_teams(mock, values):
    """Add teams for an organization

    This method fills multiple end points. Teams and its child endpoints (member,
     repo, membership, etc.)
    """
    teams = []
    for team in values:
        team_id = team["id"]
        team_url = os.path.join("teams", str(team_id))
        members = team.pop("members")
        repositories = team.pop("repositories")

        register_uri(mock, "GET", url=os.path.join(team_url, "members"),
                     json=[dict(login=member) for member in members])
        for username, data in members.items():
            register_uri(
                mock, "GET",
                url=os.path.join(team_url, "memberships", username),
                json=data
            )

        register_uri(mock, "GET", url=os.path.join(team_url, "repos"),
                     json=list(repositories.values()))

        teams.append(team)

    url = os.path.join("orgs", ORG_NAME, "teams")
    register_uri(mock, "GET", url=url, json=teams)


def allow_org_method(mock, method, url_extra=None):
    """Allow a specific method to be run against the base org url

    Allow a method to be applied on a url within the repo.
    Ex: to allow patch on /orgs/name/hooks/hook1
     call allow_org_method(mock, "PATCH", "hooks/hook1")
    """
    url = os.path.join("orgs", ORG_NAME)
    if url_extra:
        url = os.path.join(url, url_extra)
    register_uri(mock, method, url=url)


def allow_teams_method(mock, method, url_extra=None):
    url = os.path.join("teams")
    if url_extra:
        url = os.path.join(url, url_extra)
    register_uri(mock, method, url=url)


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
            billing_email="secret@mail.com",
            company="ACME",
            email="public@mail.com",
            location="London/Europe",
            name=ORG_NAME,
            description="Organization description"
        )

    @staticmethod
    def members():
        return dict(
            member1=dict(role="owner"),
            member2=dict(role="member"),
        )

    @staticmethod
    def teams():
        return [
            dict(
                id="team1id",
                name="team1",
                description="description1",
                privacy="closed",
                permission="push",  # TODO: is it default permission? Should be renamed?
                members=dict(
                    member1=dict(role="maintainer"),
                    member2=dict(role="member"),
                ),
                repositories=dict(
                    repo1=dict(
                        name="repo1",
                        permissions=dict(
                            pull=True,
                            push=True,
                            admin=False,
                        )
                    ),
                    repo2=dict(
                        name="repo2",
                        permissions=dict(
                            pull=True,
                            push=True,
                            admin=True,
                        )
                    ),
                ),
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
def org(gh):
    """Creates an Org instance and adds an spy attribute to check for calls"""
    ret = Organization(gh, name=ORG_NAME)
    ret._gh = Mock(wraps=ret._gh)
    ret.spy = ret._gh
    return ret


# ##########
# TEST CASES
# ##########

def test_create_org(org):
    """Create an instance of organization"""
    assert org is not None


def test_get_options(org):
    """Retrieves all options from github"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        assert org.options["name"] == ORG_NAME
        assert org.options == DF.options()


def test_set_options_no_change_no_request(org):
    """Updating options without change, triggers no request"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        org.options = DF.options()


def test_set_options_updated_single_field(org):
    """Updating options changing a field, triggers patch request"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        allow_org_method(mock, "PATCH")
        options = DF.options()
        options["description"] = "Yeah!"
        org.options = options
        org.spy.patch.assert_called_once()


def test_get_members(org):
    """Retrieve the members of the org and validate its formatting"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        add_org_members(mock, DF.members())
        assert org.members == dict(
            member1=dict(
                role="owner"
            ),
            member2=dict(
                role="member"
            ),
        )


def test_set_members_without_change(org):
    """Updating the members without a change triggers not http request to update"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        add_org_members(mock, DF.members())
        org.members = dict(
            member1=dict(
                role="owner"
            ),
            member2=dict(
                role="member"
            ),
        )


def test_set_members_add_one(org):
    """Adding a member calls the github api via put"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        add_org_members(mock, DF.members())
        allow_org_method(mock, "PUT", "memberships/member3")
        org.members = dict(
            member1=dict(
                role="owner"
            ),
            member2=dict(
                role="member"
            ),
            member3=dict(
                role="member"
            ),
        )
        org.spy.put.assert_called_once_with(ANY, dict(
            role="member",
        ))


def test_set_members_update_membership(org):
    """Updating a member calls the github api via put"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        add_org_members(mock, DF.members())
        allow_org_method(mock, "PUT", "memberships/member2")
        org.members = dict(
            member1=dict(
                role="owner"
            ),
            member2=dict(
                role="owner"
            ),
        )
        org.spy.put.assert_called_once_with(ANY, dict(
            role="owner",
        ))


def test_set_members_delete_one(org):
    """Removing a member calls the github api via delete"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        add_org_members(mock, DF.members())
        allow_org_method(mock, "DELETE", "members/member2")
        org.members = dict(
            member1=dict(
                role="owner"
            ),
        )
        org.spy.delete.assert_called_once()


def test_get_teams(org):
    """Retrieve a team"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        add_org_teams(mock, DF.teams())
        result = org.teams
        assert result == {
            'team1': {
                'description': 'description1',
                'members': {
                    'member1': {'role': 'maintainer'},
                    'member2': {'role': 'member'}
                },
                'permission': 'push',
                'privacy': 'closed',
                'repositories': {
                    'repo1': {'permission': 'push'},
                    'repo2': {'permission': 'admin'}
                }
            }
        }


def test_set_teams_without_change(org):
    """Updating the teams without a change triggers not http request to update"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        add_org_teams(mock, DF.teams())
        org.teams = {
            'team1': {
                'description': 'description1',
                'members': {
                    'member1': {'role': 'maintainer'},
                    'member2': {'role': 'member'}
                },
                'permission': 'push',
                'privacy': 'closed',
                'repositories': {
                    'repo1': {'permission': 'push'},
                    'repo2': {'permission': 'admin'}
                }
            }
        }


def test_set_team_delete_one(org):
    """Removing a team calls delete on it"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        add_org_teams(mock, DF.teams())
        register_uri(mock, "DELETE", url="teams/team1id")

        org.teams = {}

        org.spy.delete.assert_called_once()


def test_set_team_add_one(org):
    """Adding a team calls multiple endpoints"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        add_org_teams(mock, DF.teams())
        register_uri(mock, "POST", url="orgs/ORG_NAME/teams", json=dict(id="team2id"))
        register_uri(mock, "PUT", url="teams/team2id/repos/ORG_NAME/repo2")
        register_uri(mock, "PUT", url="teams/team2id/memberships/member2")

        org.teams = {
            'team1': {
                'description': 'description1',
                'members': {
                    'member1': {'role': 'maintainer'},
                    'member2': {'role': 'member'}
                },
                'permission': 'push',
                'privacy': 'closed',
                'repositories': {
                    'repo1': {'permission': 'push'},
                    'repo2': {'permission': 'admin'}
                }
            },
            'team2': {
                'description': 'description2',
                'members': {
                    'member2': {'role': 'member'},
                },
                'permission': 'admin',
                'privacy': 'closed',
                'repositories': {
                    'repo2': {'permission': 'push'},
                }
            }
        }

        org.spy.post.assert_called_once_with(ANY, {
            'name': 'team2',
            'description': 'description2',
            'permission': 'admin',
            'privacy': 'closed',
        })
        org.spy.put.assert_any_call(ANY, {
            "role": "member"
        })
        org.spy.put.assert_any_call(ANY, {
            "permission": "push"
        })


@pytest.mark.xfail(reason="Work in progress", run=False)
def test_set_team_update(org):
    """Adding and removing members and repos to a team"""
    with requests_mock.Mocker() as mock:
        add_org_options(mock, DF.options())
        add_org_teams(mock, DF.teams())
        register_uri(mock, "PUT", url="teams/team2id/repos/ORG_NAME/repo2")
        register_uri(mock, "PUT", url="teams/team2id/memberships/member2")

        org.teams = {
            'team1': {
                'description': 'description1',
                'id': 'team1id',
                'members': {
                    'member1': {'role': 'maintainer'},
                    'member3': {'role': 'member'}
                },
                'permission': 'push',
                'privacy': 'closed',
                'repositories': {
                    'repo1': {'permission': 'push'},
                    'repo3': {'permission': 'admin'}
                }
            },
        }

        org.spy.put.assert_any_call(ANY, {
            "role": "member"
        })
        org.spy.put.assert_any_call(ANY, {
            "permission": "push"
        })


def test_get_hooks(org):
    pass
