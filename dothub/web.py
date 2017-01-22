import flask
import werkzeug.exceptions
import logging
import os
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


@app.route("/github", methods=['POST'])
def github():
    """Main function that handles all github hook events"""
    actions = []  # Actions to perform
    try:
        event = flask.request.headers['X-GitHub-Event']
        data = flask.request.get_json() or {}
        repo_full_name = data["repository"]["full_name"]
        repo_owner = data["repository"]["owner"]["name"]
        repo_name = data["repository"]["name"]
    except KeyError:
        LOG.info("Missing data in request, rejecting", exc_info=True)
        raise werkzeug.exceptions.BadRequest("Missing data on request,"
                                             " Are you a GitHub hook event?")

    LOG.info("Handling {} event for {}".format(event, repo_full_name))

    # This code needs quite a refactor, it is late and I just want to sleep...
    # I know, so unprofessional...

    # REPO
    repo_changes = False
    repo = Repo(GH_HELPER, repo_owner, repo_name)
    try:
        file_repo_config = yaml.safe_load(repo.get_file(REPO_CONFIG_FILE))
    except requests.exceptions.HTTPError:
        pass
    else:
        current_repo_config = repo.describe()
        repo_changes = check_changes(current_repo_config, file_repo_config)

    # ORG
    org_changes = False
    try:
        org = Organization(GH_HELPER, repo_owner)
    except requests.exceptions.HTTPError:
        pass
    else:
        try:
            file_org_config = yaml.safe_load(repo.get_file(ORG_CONFIG_FILE))
        except requests.exceptions.HTTPError:
            return False
        else:
            current_org_config = org.describe()
            LOG.info("Checking if any org change...")
            org_changes = check_changes(current_org_config, file_org_config)

    if event == "push":
        if repo_changes:
            repo.update(file_repo_config)
            actions.append("repo_update")

        if org_changes:
            org.update(file_org_config)
            actions.append("org_update")

    else:  # any other hook
        if repo_changes:
            for key in [_ for _ in current_repo_config if _ not in file_repo_config]:
                current_repo_config.pop(key)
            LOG.info("Updating repo config file")
            repo.update_file(REPO_CONFIG_FILE, utils.serialize_yaml(current_repo_config))
            actions.append("repo_sync")

        if org_changes:
            for key in [_ for _ in current_org_config if _ not in file_org_config]:
                current_org_config.pop(key)
            org.update(current_org_config)
            LOG.info("Updating org config file")
            repo.update_file(ORG_CONFIG_FILE, utils.serialize_yaml(current_org_config))
            actions.append("org_sync")


    return flask.jsonify(
        success=True,
        repo=repo_full_name,
        actions=actions
    )
