# Notes:
# - Add unit and integration tests for the organization

# - Add IDs on objects that have it to allow for proper rename (labels?)
# - Define the version of the github api to use (through the media type)

import functools
import os
from . import dict_diff, utils


FIELDS = {
    "options": ["billing_email", "company", "email", "location", "name", "description"],
    # default_repository_permission, members_can_create_repositories
    "member": ["login"],
    "membership": ["role"],
    "team": ["id", "name", "description", "privacy", "permission"],
    "team_member": ["login"],
    "team_membership": ["role"],
    "team_repos": ["permissions", "name"],
    "hooks": ["name", "events", "active"],  # config might have masked secret
}


class Organization(object):
    """Object to syncs the configuration for a github organization"""

    def __init__(self, github_handle, name):
        """Creates an Organization object given the github api handle and the org name

        :param github_handle: Helper to use the github api
        :type github_handle: dothub.github_helper.Github
        :param name: name of the organization to sync
        :type name: str
        """
        self._gh = github_handle
        self.name = name

    @staticmethod
    def _get_team_url(team_id, *url_parts):
        url_parts = ["teams", str(team_id)] + list(url_parts)
        # join as paths and trash the last forward slash if any
        res = functools.reduce(os.path.join, url_parts)
        return res[:-1] if res[-1] == '/' else res

    def _get_url(self, *url_parts):
        """Given some url parts that are part of a repo returns the full url path

        _get_url("cool", "secret") -> /orgs/<owner>/cool/secret

        :rtype: str
        """
        url_parts = ["orgs", self.name] + list(url_parts)
        # join as paths and trash the last forward slash if any
        res = functools.reduce(os.path.join, url_parts)
        return res[:-1] if res[-1] == '/' else res

    @property
    def options(self):
        """General configuration of the organization"""
        url = self._get_url()
        return self._gh.get(url, FIELDS["options"])

    @options.setter
    def options(self, new):
        """Updates the organization """
        current = self.options
        if current == new:
            return

        url = self._get_url()
        self._gh.patch(url, new)

    @property
    def members(self):
        """Retrieve the plain members of an organization.

        These memebers don't need to be linked to any team but for an user to
        be added to a team they need to be in this list"""
        result = dict()
        url = self._get_url("members")
        members = self._gh.get(url, FIELDS["member"])
        for member in members:
            member_name = member["login"]
            member_url = self._get_url("memberships", member_name)
            member_fields = self._gh.get(member_url, FIELDS["membership"])
            result[member_name] = dict(role=member_fields["role"])
        return result

    @members.setter
    def members(self, new):
        current = self.members
        added, missing, updated = dict_diff.diff(current, new)
        for member_name in missing:
            url = self._get_url("members", member_name)
            self._gh.delete(url)

        for member_name in updated.union(added):
            member = new[member_name]
            url = self._get_url("memberships", member_name)
            self._gh.put(url, member)

    @property
    def teams(self):
        """Full configuration of all the teams in the org

        This contains a list of teams with their members, repos and respective permissions
        """
        result = dict()
        url = self._get_url("teams")
        teams = self._gh.get(url, FIELDS["team"])
        for team in teams:
            team_name = team.pop("name")
            team["members"] = {}
            team["repositories"] = {}
            team_id = team["id"]
            members_url = self._get_team_url(team_id, "members")
            members = self._gh.get(members_url, FIELDS["team_member"])
            for member in members:
                member_name = member.pop("login")
                membership_url = self._get_team_url(team_id, "memberships", member_name)
                membership = self._gh.get(membership_url, FIELDS["team_membership"])
                team["members"][member_name] = membership

            repos_url = self._get_team_url(team_id, "repos")
            repos = self._gh.get(repos_url, FIELDS["team_repos"])
            for repo in repos:
                repo_name = repo.pop("name")
                permissions = repo.pop("permissions")
                permission = utils.decode_permissions(permissions)
                repo["permission"] = permission
                team["repositories"][repo_name] = repo

            result[team_name] = team

        return result

    @teams.setter
    def teams(self, new):
        current = self.teams
        added, missing, updated = dict_diff.diff(current, new)

        for team_name in missing:
            team_id = current[team_name]["id"]
            url = self._get_team_url(team_id)
            self._gh.delete(url)

        for team_name in added:
            team = new[team_name]
            repos = team.pop("repositories", {})
            members = team.pop("members", {})
            team["name"] = team_name

            url = self._get_url("teams")
            team_id = self._gh.post(url, team)["id"]

            for repo_name, repo in repos.items():
                url = self._get_team_url(team_id, "repos", self.name, repo_name)
                self._gh.put(url, repo)

            for member_name, member in members.items():
                url = self._get_team_url(team_id, "memberships", member_name)
                self._gh.put(url, member)

        for team_name in updated:
            new_team = new[team_name]
            old_team = new[team_name]
            team_id = new_team.pop("id")
            if team_id != old_team.pop("id"):
                raise RuntimeError("Cannot update the team id")
            new_repos = new_team.pop("repositories", {})
            old_repos = old_team.pop("repositories", {})
            new_members = new_team.pop("members", {})
            old_members = old_team.pop("members", {})

            if old_team != new_team:
                url = self._get_team_url(team_id)
                self._gh.patch(url, new_team)

            # update repos
            r_added, r_missing, r_updated = dict_diff.diff(old_repos, new_repos)
            for repo_name in r_added.union(r_updated):
                repo = new_repos[repo_name]
                url = self._get_team_url(team_id, "repos", self.name, repo_name)
                self._gh.put(url, repo)

            for repo_name in r_missing:
                url = self._get_team_url(team_id, "repos", self.name, repo_name)
                self._gh.delete(url)

            # update members
            m_added, m_missing, m_updated = dict_diff.diff(old_members, new_members)
            for member_name in m_added.union(m_updated):
                member = new_members[member_name]
                url = self._get_team_url(team_id, "memberships", member_name)
                self._gh.put(url, member)

            for member_name in m_missing:
                url = self._get_team_url(team_id, "memberships", member_name)
                self._gh.delete(url)

    @property
    def hooks(self):
        """Retrieve the organization level web hooks"""
        result = dict()
        url = self._get_url("hooks")
        hooks = self._gh.get(url, FIELDS["hooks"])
        for hook in hooks:
            result[hook.pop("name")] = hook

        return result

    @hooks.setter
    def hooks(self, new):
        current = self.hooks
        raw_curr_hooks = self._gh.get(self._get_url("hooks"), ["name", "id"])
        hooks_id = {h["name"]: h["id"] for h in raw_curr_hooks}

        added, missing, updated = dict_diff.diff(current, new)
        for hook_name in missing:
            hook_id = hooks_id[hook_name]
            url = self._get_url("hooks", hook_id)
            self._gh.delete(url)

        for hook_name in updated:
            hook_id = hooks_id[hook_name]
            hook = new[hook_name]
            url = self._get_url("hooks", hook_id)
            self._gh.patch(url, hook)

        if added:
            raise RuntimeError("Adding hooks still not supported: {}".format(added))

    def describe(self):
        """Serializes the whole configuration into a dict"""
        return dict(
            options=self.options,
            members=self.members,
            teams=self.teams,
            hooks=self.hooks
        )

    def update(self, data):
        """Updates the github configuration with the configuration data passed in """
        self.options = data["options"]
        self.members = data["members"]
        self.teams = data["teams"]
        self.hooks = data["hooks"]


