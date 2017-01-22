import os.path
import functools
from . import dict_diff, utils
import base64

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
            "name", "events", "active", "config"
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
        url_parts = ["repos", self.owner, self.repository] + [str(p) for p in url_parts]
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
            if "secret" or "token" in hook:
                raise RuntimeError("Updating hooks with secrets is not supported")
            url = self._get_url("hooks", hook_id)
            self._gh.patch(url, hook)

        for hook_name in added:
            hook = new[hook_name]
            url = self._get_url("hooks")
            self._gh.post(url, hook)

    def describe(self):
        config = dict()
        config["options"] = self.options
        config["collaborators"] = self.collaborators
        config["labels"] = self.labels
        config["hooks"] = self.hooks
        return config

    def update(self, config):
        if "options" in config:
            self.options = config["options"]
        if "collaborators" in config:
            self.collaborators = config["collaborators"]
        if "labels" in config:
            self.labels = config["labels"]
        if "hooks" in config:
            self.hooks = config["hooks"]

    def get_file(self, file_path):
        """Retrieves a file from the repo

        :param file_path: File to retrieve content from the repo
        """
        url = self._get_url("contents", file_path)
        encoded_content = self._gh.get(url, ["content"])["content"]
        return base64.b64decode(encoded_content)

    def update_file(self, file_path, content):
        """Updates a file from the repo with the passed content

        :param file_path: File to retrieve content from the repo
        :param content: New content of the file
        """
        url = self._get_url("contents", file_path)
        file_sha = self._gh.get(url, ["sha"])["sha"]
        encoded_content = base64.b64encode(content)
        self._gh.patch(url, {
            "path": file_path,
            "message": "dobhub auto sync",
            "content": encoded_content,
            "sha": file_sha
        })
