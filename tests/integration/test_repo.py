"""Integration tests for repository control"""
from .regex_dict import RegExDict
from click.testing import CliRunner
from dothub._main import dothub
import copy
import yaml
import tempfile
import sealedmock
from mock import Mock


base_args = ["--user=xxx", "--token=yyy"]


GET_REQUESTS = RegExDict({
    "^.*/repos/[^/]+/[^/]*$": {u'issues_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/issues{/number}', u'deployments_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/deployments', u'stargazers_count': 0, u'forks_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/forks', u'mirror_url': None, u'subscription_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/subscription', u'notifications_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/notifications{?since,all,participating}', u'collaborators_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/collaborators{/collaborator}', u'updated_at': u'2016-09-27T19:31:26Z', u'private': False, u'pulls_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/pulls{/number}', u'issue_comment_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/issues/comments{/number}', u'labels_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/labels{/name}', u'has_wiki': True, u'full_name': u'Mariocj89/echaloasuerte', u'owner': {u'following_url': u'https://api.github.com/users/Mariocj89/following{/other_user}', u'events_url': u'https://api.github.com/users/Mariocj89/events{/privacy}', u'organizations_url': u'https://api.github.com/users/Mariocj89/orgs', u'url': u'https://api.github.com/users/Mariocj89', u'gists_url': u'https://api.github.com/users/Mariocj89/gists{/gist_id}', u'html_url': u'https://github.com/Mariocj89', u'subscriptions_url': u'https://api.github.com/users/Mariocj89/subscriptions', u'avatar_url': u'https://avatars.githubusercontent.com/u/3709683?v=3', u'repos_url': u'https://api.github.com/users/Mariocj89/repos', u'received_events_url': u'https://api.github.com/users/Mariocj89/received_events', u'gravatar_id': u'', u'starred_url': u'https://api.github.com/users/Mariocj89/starred{/owner}{/repo}', u'site_admin': False, u'login': u'Mariocj89', u'type': u'User', u'id': 3709683, u'followers_url': u'https://api.github.com/users/Mariocj89/followers'}, u'statuses_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/statuses/{sha}', u'id': 31619639, u'keys_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/keys{/key_id}', u'description': None, u'subscribers_count': 1, u'tags_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/tags', u'network_count': 4, u'downloads_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/downloads', u'assignees_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/assignees{/user}', u'contents_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/contents/{+path}', u'has_pages': False, u'git_refs_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/git/refs{/sha}', u'open_issues_count': 0, u'source': {u'issues_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/issues{/number}', u'deployments_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/deployments', u'stargazers_count': 4, u'forks_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/forks', u'mirror_url': None, u'subscription_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/subscription', u'notifications_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/notifications{?since,all,participating}', u'collaborators_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/collaborators{/collaborator}', u'updated_at': u'2016-11-18T00:32:35Z', u'private': False, u'pulls_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/pulls{/number}', u'issue_comment_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/issues/comments{/number}', u'labels_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/labels{/name}', u'has_wiki': False, u'full_name': u'etcaterva/echaloasuerte', u'owner': {u'following_url': u'https://api.github.com/users/etcaterva/following{/other_user}', u'events_url': u'https://api.github.com/users/etcaterva/events{/privacy}', u'organizations_url': u'https://api.github.com/users/etcaterva/orgs', u'url': u'https://api.github.com/users/etcaterva', u'gists_url': u'https://api.github.com/users/etcaterva/gists{/gist_id}', u'html_url': u'https://github.com/etcaterva', u'subscriptions_url': u'https://api.github.com/users/etcaterva/subscriptions', u'avatar_url': u'https://avatars.githubusercontent.com/u/11301498?v=3', u'repos_url': u'https://api.github.com/users/etcaterva/repos', u'received_events_url': u'https://api.github.com/users/etcaterva/received_events', u'gravatar_id': u'', u'starred_url': u'https://api.github.com/users/etcaterva/starred{/owner}{/repo}', u'site_admin': False, u'login': u'etcaterva', u'type': u'Organization', u'id': 11301498, u'followers_url': u'https://api.github.com/users/etcaterva/followers'}, u'statuses_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/statuses/{sha}', u'id': 23440601, u'keys_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/keys{/key_id}', u'description': None, u'tags_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/tags', u'downloads_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/downloads', u'assignees_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/assignees{/user}', u'contents_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/contents/{+path}', u'has_pages': False, u'git_refs_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/git/refs{/sha}', u'open_issues_count': 5, u'clone_url': u'https://github.com/etcaterva/echaloasuerte.git', u'watchers_count': 4, u'git_tags_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/git/tags{/sha}', u'milestones_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/milestones{/number}', u'languages_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/languages', u'size': 7365, u'homepage': u'https://echaloasuerte.com', u'fork': False, u'commits_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/commits{/sha}', u'releases_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/releases{/id}', u'issue_events_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/issues/events{/number}', u'archive_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/{archive_format}{/ref}', u'comments_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/comments{/number}', u'events_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/events', u'contributors_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/contributors', u'html_url': u'https://github.com/etcaterva/echaloasuerte', u'forks': 4, u'compare_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/compare/{base}...{head}', u'open_issues': 5, u'git_url': u'git://github.com/etcaterva/echaloasuerte.git', u'svn_url': u'https://github.com/etcaterva/echaloasuerte', u'merges_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/merges', u'has_issues': True, u'ssh_url': u'git@github.com:etcaterva/echaloasuerte.git', u'blobs_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/git/blobs{/sha}', u'git_commits_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/git/commits{/sha}', u'hooks_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/hooks', u'has_downloads': True, u'watchers': 4, u'name': u'echaloasuerte', u'language': u'Python', u'url': u'https://api.github.com/repos/etcaterva/echaloasuerte', u'created_at': u'2014-08-28T19:40:10Z', u'pushed_at': u'2016-11-18T00:32:34Z', u'forks_count': 4, u'default_branch': u'master', u'teams_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/teams', u'trees_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/git/trees{/sha}', u'branches_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/branches{/branch}', u'subscribers_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/subscribers', u'stargazers_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/stargazers'}, u'clone_url': u'https://github.com/Mariocj89/echaloasuerte.git', u'watchers_count': 0, u'git_tags_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/git/tags{/sha}', u'milestones_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/milestones{/number}', u'languages_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/languages', u'size': 7267, u'homepage': u'', u'fork': True, u'commits_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/commits{/sha}', u'releases_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/releases{/id}', u'issue_events_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/issues/events{/number}', u'parent': {u'issues_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/issues{/number}', u'deployments_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/deployments', u'stargazers_count': 4, u'forks_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/forks', u'mirror_url': None, u'subscription_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/subscription', u'notifications_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/notifications{?since,all,participating}', u'collaborators_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/collaborators{/collaborator}', u'updated_at': u'2016-11-18T00:32:35Z', u'private': False, u'pulls_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/pulls{/number}', u'issue_comment_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/issues/comments{/number}', u'labels_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/labels{/name}', u'has_wiki': False, u'full_name': u'etcaterva/echaloasuerte', u'owner': {u'following_url': u'https://api.github.com/users/etcaterva/following{/other_user}', u'events_url': u'https://api.github.com/users/etcaterva/events{/privacy}', u'organizations_url': u'https://api.github.com/users/etcaterva/orgs', u'url': u'https://api.github.com/users/etcaterva', u'gists_url': u'https://api.github.com/users/etcaterva/gists{/gist_id}', u'html_url': u'https://github.com/etcaterva', u'subscriptions_url': u'https://api.github.com/users/etcaterva/subscriptions', u'avatar_url': u'https://avatars.githubusercontent.com/u/11301498?v=3', u'repos_url': u'https://api.github.com/users/etcaterva/repos', u'received_events_url': u'https://api.github.com/users/etcaterva/received_events', u'gravatar_id': u'', u'starred_url': u'https://api.github.com/users/etcaterva/starred{/owner}{/repo}', u'site_admin': False, u'login': u'etcaterva', u'type': u'Organization', u'id': 11301498, u'followers_url': u'https://api.github.com/users/etcaterva/followers'}, u'statuses_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/statuses/{sha}', u'id': 23440601, u'keys_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/keys{/key_id}', u'description': None, u'tags_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/tags', u'downloads_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/downloads', u'assignees_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/assignees{/user}', u'contents_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/contents/{+path}', u'has_pages': False, u'git_refs_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/git/refs{/sha}', u'open_issues_count': 5, u'clone_url': u'https://github.com/etcaterva/echaloasuerte.git', u'watchers_count': 4, u'git_tags_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/git/tags{/sha}', u'milestones_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/milestones{/number}', u'languages_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/languages', u'size': 7365, u'homepage': u'https://echaloasuerte.com', u'fork': False, u'commits_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/commits{/sha}', u'releases_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/releases{/id}', u'issue_events_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/issues/events{/number}', u'archive_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/{archive_format}{/ref}', u'comments_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/comments{/number}', u'events_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/events', u'contributors_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/contributors', u'html_url': u'https://github.com/etcaterva/echaloasuerte', u'forks': 4, u'compare_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/compare/{base}...{head}', u'open_issues': 5, u'git_url': u'git://github.com/etcaterva/echaloasuerte.git', u'svn_url': u'https://github.com/etcaterva/echaloasuerte', u'merges_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/merges', u'has_issues': True, u'ssh_url': u'git@github.com:etcaterva/echaloasuerte.git', u'blobs_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/git/blobs{/sha}', u'git_commits_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/git/commits{/sha}', u'hooks_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/hooks', u'has_downloads': True, u'watchers': 4, u'name': u'echaloasuerte', u'language': u'Python', u'url': u'https://api.github.com/repos/etcaterva/echaloasuerte', u'created_at': u'2014-08-28T19:40:10Z', u'pushed_at': u'2016-11-18T00:32:34Z', u'forks_count': 4, u'default_branch': u'master', u'teams_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/teams', u'trees_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/git/trees{/sha}', u'branches_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/branches{/branch}', u'subscribers_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/subscribers', u'stargazers_url': u'https://api.github.com/repos/etcaterva/echaloasuerte/stargazers'}, u'archive_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/{archive_format}{/ref}', u'comments_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/comments{/number}', u'events_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/events', u'contributors_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/contributors', u'html_url': u'https://github.com/Mariocj89/echaloasuerte', u'forks': 0, u'compare_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/compare/{base}...{head}', u'open_issues': 0, u'git_url': u'git://github.com/Mariocj89/echaloasuerte.git', u'svn_url': u'https://github.com/Mariocj89/echaloasuerte', u'merges_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/merges', u'has_issues': False, u'ssh_url': u'git@github.com:Mariocj89/echaloasuerte.git', u'blobs_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/git/blobs{/sha}', u'git_commits_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/git/commits{/sha}', u'hooks_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/hooks', u'has_downloads': True, u'watchers': 0, u'name': u'echaloasuerte', u'language': u'Python', u'url': u'https://api.github.com/repos/Mariocj89/echaloasuerte', u'created_at': u'2015-03-03T20:28:26Z', u'pushed_at': u'2016-11-17T22:25:54Z', u'forks_count': 0, u'default_branch': u'master', u'teams_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/teams', u'trees_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/git/trees{/sha}', u'branches_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/branches{/branch}', u'subscribers_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/subscribers', u'permissions': {u'admin': True, u'push': True, u'pull': True}, u'stargazers_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/stargazers'},
    "^.*repos/[^/]*/[^/]*/collaborators$": [{u'following_url': u'https://api.github.com/users/Mariocj89/following{/other_user}', u'events_url': u'https://api.github.com/users/Mariocj89/events{/privacy}', u'organizations_url': u'https://api.github.com/users/Mariocj89/orgs', u'url': u'https://api.github.com/users/Mariocj89', u'gists_url': u'https://api.github.com/users/Mariocj89/gists{/gist_id}', u'html_url': u'https://github.com/Mariocj89', u'subscriptions_url': u'https://api.github.com/users/Mariocj89/subscriptions', u'avatar_url': u'https://avatars.githubusercontent.com/u/3709683?v=3', u'repos_url': u'https://api.github.com/users/Mariocj89/repos', u'received_events_url': u'https://api.github.com/users/Mariocj89/received_events', u'gravatar_id': u'', u'starred_url': u'https://api.github.com/users/Mariocj89/starred{/owner}{/repo}', u'site_admin': False, u'login': u'Mariocj89', u'type': u'User', u'id': 3709683, u'followers_url': u'https://api.github.com/users/Mariocj89/followers', u'permissions': {u'admin': True, u'push': True, u'pull': True}}],
    "^.*repos/[^/]*/[^/]*/labels$": [{u'url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/labels/bug', u'color': u'fc2929', u'default': True, u'id': 182909020, u'name': u'bug'}, {u'url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/labels/duplicate', u'color': u'cccccc', u'default': True, u'id': 182909021, u'name': u'duplicate'}, {u'url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/labels/enhancement', u'color': u'84b6eb', u'default': True, u'id': 182909022, u'name': u'enhancement'}, {u'url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/labels/help%20wanted', u'color': u'159818', u'default': True, u'id': 182909023, u'name': u'help wanted'}, {u'url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/labels/invalid', u'color': u'e6e6e6', u'default': True, u'id': 182909024, u'name': u'invalid'}, {u'url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/labels/question', u'color': u'cc317c', u'default': True, u'id': 182909025, u'name': u'question'}, {u'url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/labels/wontfix', u'color': u'ffffff', u'default': True, u'id': 182909026, u'name': u'wontfix'}],
    "^.*repos/[^/]*/[^/]*/hooks$": [{u'name': u'travis', u'url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/hooks/4288233', u'type': u'Repository', u'created_at': u'2015-03-08T14:37:13Z', u'updated_at': u'2016-03-25T19:02:03Z', u'test_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/hooks/4288233/test', u'id': 4288233, u'ping_url': u'https://api.github.com/repos/Mariocj89/echaloasuerte/hooks/4288233/pings', u'active': False, u'config': {u'domain': u'notify.travis-ci.org', u'token': u'********', u'user': u'Mariocj89'}, u'events': [u'issue_comment', u'member', u'public', u'pull_request', u'push'], u'last_response': {u'status': u'active', u'message': u'OK', u'code': 200}}],
})

EXPECTED_RESULT = """collaborators:
  Mariocj89:
    permissions:
      admin: true
      pull: true
      push: true
hooks:
  travis:
    active: false
    events:
    - issue_comment
    - member
    - public
    - pull_request
    - push
labels:
  bug:
    color: fc2929
  duplicate:
    color: cccccc
  enhancement:
    color: 84b6eb
  help wanted:
    color: '159818'
  invalid:
    color: e6e6e6
  question:
    color: cc317c
  wontfix:
    color: ffffff
options:
  description: null
  has_downloads: true
  has_issues: false
  has_wiki: true
  homepage: ''
  name: echaloasuerte
  private: false
"""


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
        args = base_args + ["repo", "--organization=org", "--repository=repo", "pull",
                            "--output_file=" + file_.name]
        result = runner.invoke(dothub, args, obj={})

        assert 0 == result.exit_code
        with open(file_.name) as f:
            result_config = f.read()
        assert EXPECTED_RESULT == result_config


@sealedmock.patch("dothub._main.github_helper.requests.Session")
def test_repo_push_without_changes(session_mock):
    runner = CliRunner()
    session_mock.return_value.get.side_effect = get_mock_response
    session_mock.sealed = True
    with tempfile.NamedTemporaryFile() as file_:
        with open(file_.name, 'w') as f:
            f.write(EXPECTED_RESULT)

        args = base_args + ["repo", "--organization=org", "--repository=repo", "push",
                            "--input_file=" + file_.name]
        result = runner.invoke(dothub, args, obj={})

        assert 0 == result.exit_code
    # session put/patch/delete were not called


@sealedmock.patch("dothub._main.github_helper.requests.Session")
def test_repo_push_with_changes(session_mock):
    runner = CliRunner()
    session_mock.return_value.get.side_effect = get_mock_response
    session_mock.return_value.post.return_value = Mock()
    session_mock.return_value.patch.return_value = Mock()
    session_mock.return_value.put.return_value = Mock()
    session_mock.return_value.delete.return_value = Mock()
    session_mock.sealed = True

    new_config = yaml.safe_load(EXPECTED_RESULT)
    # Rename collaborator
    new_config['collaborators']['new_collaborators'] = new_config['collaborators'].pop("Mariocj89")

    # Rename label
    new_config["labels"]["cool_bug"] = new_config["labels"].pop("bug")
    # Update label
    new_config["labels"]["question"]["color"] = "000000"

    # Update options
    new_config["options"]["description"] = "Yet a cooler description"

    with tempfile.NamedTemporaryFile() as file_:
        with open(file_.name, 'w') as f:
            yaml.safe_dump(new_config, f, encoding='utf-8', allow_unicode=True,
                           default_flow_style=False)

        args = base_args + ["repo", "--organization=org", "--repository=repo", "push",
                            "--input_file=" + file_.name]
        result = runner.invoke(dothub, args, obj={})

    assert 0 == result.exit_code
    assert 1 == session_mock.return_value.post.call_count  # Renamed label
    assert 1 == session_mock.return_value.put.call_count  # Renamed collaborator
    assert 2 == session_mock.return_value.delete.call_count  # Renamed label & collaborator
    assert 2 == session_mock.return_value.patch.call_count  # updated description + label

