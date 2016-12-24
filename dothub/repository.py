import os.path
import functools
from . import dict_diff, utils

FIELDS = {
    "repo": {
        "options": [
            "name", "description", "homepage", "private", "has_issues", "has_wiki",
            "has_downloads", "allow_rebase_merge", "allow_squash_merge",
            "allow_merge_commit"
        ],
        "label": [
            "name", "color"
        ],
        "collaborator": [
            "login", "permissions"
        ],
        "hooks": [
            "name", "events", "active"
        ]
    }
}


class Repo(object):
    """Represents an repository on github.

    It helps to retrieve the repository configuration and all of its
    elements
    """
    def __init__(self, github, owner, repository):
        """Creates a repo object

        :param github: Github helper to handle communications with the API
        :type github: dothub.github_helper.Github
        :param owner: owner of the repository
        :type owner: str
        :param repository: repository name in github
        :type repository: str
        """
        self._gh = github
        self.owner = owner
        self.repository = repository

    def _get_url(self, *url_parts):
        """Given some url parts that are part of a repo returns the full url path

        _get_url("cool", "secret") -> /repos/<owner>/<repo_name>/cool/secret

        :rtype: str
        """
        url_parts = ["repos", self.owner, self.repository] + list(url_parts)
        # join as paths and trash the last forward slash if any
        res = functools.reduce(os.path.join, url_parts)
        return res[:-1] if res[-1] == '/' else res

    @property
    def options(self):
        """The main options of the repo

        Name, description, url, etc...
        """
        url = self._get_url("")
        return self._gh.get(url, FIELDS["repo"]["options"])

    @options.setter
    def options(self, new):
        current = self.options
        if current == new:
            return

        url = self._get_url("")
        self._gh.patch(url, new)

    @property
    def labels(self):
        """List of issue labels"""
        url = self._get_url("labels")
        result = dict()
        for label in self._gh.get(url, FIELDS["repo"]["label"]):
            name = label.pop("name")
            result[name] = label
        return result

    @labels.setter
    def labels(self, new):
        current = self.labels
        added, missing, updated = dict_diff.diff(current, new)
        for label in added:
            new_label = new[label]
            new_label["name"] = label
            url = self._get_url("labels")
            self._gh.post(url, new_label)
        for label in missing:
            url = self._get_url("labels", label)
            self._gh.delete(url)
        for label in updated:
            new_label = new[label]
            new_label["name"] = label
            url = self._get_url("labels", label)
            self._gh.patch(url, new_label)

    @property
    def collaborators(self):
        """List of collaborators"""
        url = self._get_url("collaborators")
        result = dict()
        for collaborator in self._gh.get(url, FIELDS["repo"]["collaborator"]):
            name = collaborator.pop("login")
            permissions = collaborator.pop("permissions")
            permission = utils.decode_permissions(permissions)
            collaborator["permission"] = permission
            result[name] = collaborator
        return result

    @collaborators.setter
    def collaborators(self, new):
        current = self.collaborators
        added, missing, updated = dict_diff.diff(current, new)
        for user in updated:
            # Update by recreating
            missing.append(user)
            added.append(user)
        for user in missing:
            url = self._get_url("collaborators", user)
            self._gh.delete(url)
        for user in added:
            url = self._get_url("collaborators", user)
            values = new[user]
            self._gh.put(url, values)

    @property
    def hooks(self):
        """List of hooks"""
        url = self._get_url("hooks")
        result = dict()
        for hook in self._gh.get(url, FIELDS["repo"]["hooks"]):
            name = hook.pop("name")
            result[name] = hook
        return result

    @hooks.setter
    def hooks(self, new):
        current = self.hooks
        if current == new:
            return
        raise NotImplementedError("Hook edition not implemented yet")

    def describe(self):
        config = dict()
        config["options"] = self.options
        # TODO branches config
        config["collaborators"] = self.collaborators
        config["labels"] = self.labels
        config["hooks"] = self.hooks
        return config

    def update(self, config):
        self.options = config["options"]
        # TODO branches config
        self.collaborators = config["collaborators"]
        self.labels = config["labels"]
        self.hooks = config["hooks"]

