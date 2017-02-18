import flask
import werkzeug.exceptions
import logging
import os
import itertools
from dothub.repository import Repo
from dothub.organization import Organization
from dothub import github_helper
from dothub.cli import REPO_CONFIG_FILE, ORG_CONFIG_FILE, ORG_REPOS_CONFIG_FILE
from dothub import utils
import requests.exceptions
import yaml

logging.basicConfig(level=logging.INFO)

LOG = logging.getLogger(__name__)


def init_gh_helper():
    user = os.environ["DOTHUB_USER"]
    token = os.environ["DOTHUB_TOKEN"]
    url = os.environ.get("DOTHUB_API_URL", github_helper.DEFAULT_API_URL)
    logging.info("Using github user '{}' and targetting api '{}'".format(user, url))
    return github_helper.GitHub(user, token, url)


GH_HELPER = init_gh_helper()
app = flask.Flask(__name__)
app.config['DEBUG'] = bool(os.environ.get("DOTHUB_DEBUG"))  # True if set to anything


def check_changes(current, new):
    """Logs the changes on the config and return True if any"""
    added, removed, changed = utils.diff_configs(current, new)

    if not(added or removed or changed):
        LOG.info("No Changes")
        return False

    LOG.info("Changes: ")
    for l in added:
        LOG.info("+ {}".format(l))
    for l in removed:
        LOG.info("- {}".format(l))
    for l, v in changed.items():
        LOG.info("C {0} ({1[old_value]} -> {1[new_value]})".format(l, v))
    return True


@app.route("/")
def index():
    return "TODO"


def repo_update(org, repo):
    """Updates the repo configuration using the dothub file in it"""
    repo = Repo(GH_HELPER, org, repo)
    try:
        file_repo_config = yaml.safe_load(repo.get_file(REPO_CONFIG_FILE))
    except requests.exceptions.HTTPError:
        pass
    else:
        current_repo_config = repo.describe()
        LOG.info("Checking if any repo changes")
        if check_changes(current_repo_config, file_repo_config):
            LOG.info("Updating repo configuration")
            repo.update(file_repo_config)
            return ["repo_update"]
    return []


def repo_sync(org, repo):
    """Updates the file config based on the current configuration"""
    repo = Repo(GH_HELPER, org, repo)
    try:
        file_repo_config = yaml.safe_load(repo.get_file(REPO_CONFIG_FILE))
    except requests.exceptions.HTTPError:
        pass  # Don't update if there is not file already
    else:
        current_repo_config = repo.describe()
        LOG.info("Checking if any repo changes")
        if check_changes(file_repo_config, current_repo_config):
            for key in [_ for _ in current_repo_config if _ not in file_repo_config]:
                current_repo_config.pop(key)
            LOG.info("Updating repo config file")
            repo.update_file(REPO_CONFIG_FILE, utils.serialize_yaml(current_repo_config))
            return ["repo_sync"]
    return []


def org_update(org, repo):
    """Updates the oeg configuration using the dothub file in a repo"""
    repo = Repo(GH_HELPER, org, repo)
    try:
        org = Organization(GH_HELPER, org)
    except requests.exceptions.HTTPError:
        pass
    else:
        try:
            file_org_config = yaml.safe_load(repo.get_file(ORG_CONFIG_FILE))
        except requests.exceptions.HTTPError:
            pass
        else:
            current_org_config = org.describe()
            LOG.info("Checking if any org change...")
            if check_changes(current_org_config, file_org_config):
                LOG.info("Updating org configuration")
                org.update(file_org_config)
                return ["org_update"]
    return []


def org_sync(org, repo):
    """Updates the file config for the org based on the current configuration"""
    repo = Repo(GH_HELPER, org, repo)
    try:
        org = Organization(GH_HELPER, org)
    except requests.exceptions.HTTPError:
        pass  # Don't update if there is not file already
    else:
        try:
            file_org_config = yaml.safe_load(repo.get_file(ORG_CONFIG_FILE))
        except requests.exceptions.HTTPError:
            pass
        else:
            current_org_config = org.describe()
            LOG.info("Checking if any org change...")
            for key in [_ for _ in current_org_config if _ not in file_org_config]:
                current_org_config.pop(key)
            if check_changes(file_org_config, current_org_config):
                LOG.info("Updating repo config file")
                repo.update_file(REPO_CONFIG_FILE, utils.serialize_yaml(current_org_config))
                return ["org_sync"]
    return []


@app.route("/github", methods=['POST'])
def github():
    """Main function that handles all github hook events"""
    actions = []  # Actions to perform
    try:
        event = flask.request.headers['X-GitHub-Event']
        data = flask.request.get_json() or {}
    except KeyError:
        LOG.info("Missing data in request, rejecting", exc_info=True)
        raise werkzeug.exceptions.BadRequest("Missing data on request,"
                                             " Are you a GitHub hook event?")

    repo_full_name = data["repository"]["full_name"] if "repository" in data else "N/A"
    LOG.info("Handling {} event for {}".format(event, repo_full_name))

    if event == "ping":
        return "pong"

    elif event == "push":
        owner = data["repository"]["owner"]
        repo_owner = owner.get("name", owner.get("login"))
        assert repo_owner
        repo_name = data["repository"]["name"]
        updated_files = list(itertools.chain(*[c["modified"] for c in data["commits"]]))
        LOG.info(updated_files)

        # Syncing the config file is disabled due to known issues when changing both
        # can lead to a consistency issue. At the moment the only source of truth is
        # considered the config file
        if REPO_CONFIG_FILE in updated_files:
            actions += repo_update(repo_owner, repo_name)
        # else:
        #    actions += repo_sync(repo_owner, repo_name)

        if ORG_CONFIG_FILE in updated_files:
            actions += org_update(repo_owner, repo_name)
        # else:
        #    actions += org_sync(repo_owner, repo_name)

    else:  # any other hook
        if "repository" in data:
            repo_owner = data["repository"]["owner"]["name"]
            repo_name = data["repository"]["name"]
            # actions += repo_sync(repo_owner, repo_name)
            # actions += org_sync(repo_owner, repo_name)

    return flask.jsonify(
        success=True,
        repo=repo_full_name,
        actions=actions
    )
