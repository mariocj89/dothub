import os.path
import functools

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

    def _get_url(self, url):
        """Given a suburl returns the full path down to the repo
        with it appended"""
        url_parts = ["repos", self.owner, self.repository, url]
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

    @property
    def labels(self):
        """List of issue labels"""
        url = self._get_url("labels")
        result = dict()
        for label in self._gh.get(url, FIELDS["repo"]["label"]):
            name = label.pop("name")
            result[name] = label
        return result

    @property
    def collaborators(self):
        """List of collaborators"""
        url = self._get_url("collaborators")
        result = dict()
        for collaborator in self._gh.get(url, FIELDS["repo"]["collaborator"]):
            name = collaborator.pop("login")
            result[name] = collaborator
        return result

    @property
    def hooks(self):
        """List of hooks"""
        url = self._get_url("hooks")
        result = dict()
        for hook in self._gh.get(url, FIELDS["repo"]["hooks"]):
            name = hook.pop("name")
            result[name] = hook
        return result

    def describe(self):
        config = dict()
        config["options"] = self.options
        # TODO branches config
        config["collaborators"] = self.collaborators
        config["labels"] = self.labels
        config["hooks"] = self.hooks

        return config
