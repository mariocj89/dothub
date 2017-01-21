import flask
import werkzeug.exceptions
import logging
import os
from dothub.repository import Repo
from dothub import github_helper
from dothub.cli import REPO_CONFIG_FILE
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
    repo = Repo(GH_HELPER, repo_owner, repo_name)

    if event == "push":
        # REPO CONFIG
        try:
            new_config = yaml.safe_load(repo.get_file(REPO_CONFIG_FILE))
            current = repo.describe()
            LOG.info("Checking if any repo change...")
            if check_changes(current, new_config):
                repo.update(new_config)
                actions.append("repo_sync")
        except requests.exceptions.HTTPError:
            LOG.info("Skipping repo config", exc_info=True)
            pass

    return flask.jsonify(
        success=True,
        repo=repo_full_name,
        actions=actions
    )
