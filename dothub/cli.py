"""Functions for the command line interface"""

import logging
import click
import fnmatch
from dothub import github_helper
from dothub import utils
from dothub.organization import Organization
from dothub.repository import Repo
from dothub.config import config_wizard, DEFAULT_API_URL

REPO_CONFIG_FILE = ".dothub.repo.yml"
ORG_CONFIG_FILE = ".dothub.org.yml"
ORG_REPOS_CONFIG_FILE = ".dothub.org.repos.yml"
LOG = logging.getLogger(__name__)


@click.group()
@click.option("--user", help="GitHub user to use", envvar="GITHUB_USER", required=True)
@click.option("--token", help="GitHub API token to use", envvar="GITHUB_TOKEN", required=True)
@click.option("--github_base_url", help="GitHub base api url",
              envvar="GITHUB_API_URL", default=DEFAULT_API_URL)
@click.option("--verbosity", help="verbosity of the log",
              default="INFO", type=click.Choice(["ERROR", "INFO", "DEBUG"]))
@click.pass_context
def dothub(ctx, user, token, github_base_url, verbosity):
    """Configure github as code!

    Stop using the keyboard like a mere human and store your github config in a file"""
    logging.getLogger().setLevel(getattr(logging, verbosity))

    gh = github_helper.GitHub(user, token, github_base_url)
    ctx.obj['github'] = gh


@dothub.command()
def configure():
    """Runs the configuration wizard"""
    config_wizard()


@dothub.command()
@click.argument("target", required=True)
@click.argument("file_", required=False)
@click.pass_context
def pull(ctx, target, file_):
    """Pulls the configuration from the github object.

    `dothub pull organization/repository` will retrieve the repository configuration.

    `dothub pull organization` will retrieve the organization configuration.

    The config will be stored in YAML in `.dothub.repo/org.yml
    """
    gh = ctx.obj['github']
    org_name, repo_name = utils.split_org_repo(target)
    org = Organization(gh, org_name)

    if not repo_name:
        file_ = file_ or ORG_CONFIG_FILE
        LOG.info("Pulling '{}' into '{}'".format(org_name, file_))
        _pull_org(org, file_)
    else:
        repo = Repo(gh, org_name, repo_name)
        file_ = file_ or REPO_CONFIG_FILE
        LOG.info("Pulling '{}/{}' into '{}'".format(org_name, repo_name, file_))
        _pull_repo(repo, file_)


@dothub.command()
@click.argument("target", required=True)
@click.argument("file_", required=False)
@click.option(
    "--bulk",
    is_flag=True,
    help="""Updates multiple repositories in the org. Uses gob to match them.

    The repository name will be matched using glob. example: organization/start-*

    By default {} is used instead of {}
    """.format(ORG_REPOS_CONFIG_FILE, REPO_CONFIG_FILE),
)
@click.pass_context
def push(ctx, target, file_, bulk):
    """Push configuration from local files to github

    `dothub push organization/repository` will update the repository.

    `dothub push organization` will update the organization

    The config is retrieved by default from the same files used in pull
    """
    gh = ctx.obj['github']
    org_name, repo_name = utils.split_org_repo(target)

    if bulk:
        org = Organization(gh, org_name)
        file_ = file_ or ORG_REPOS_CONFIG_FILE
        LOG.info("Pushing '{}' into multiple repos: '{}'".format(org_name, file_))
        _update_all_repos(gh, org, file_, repo_name)
    elif not repo_name:
        org = Organization(gh, org_name)
        file_ = file_ or ORG_CONFIG_FILE
        LOG.info("Pulling '{}' into '{}'".format(org_name, file_))
        _push_repo(org, file_)
    else:
        repo = Repo(gh, org_name, repo_name)
        file_ = file_ or REPO_CONFIG_FILE
        LOG.info("Pulling '{}/{}' into '{}'".format(org_name, repo_name, file_))
        _push_repo(repo, file_)


def _pull_repo(repo, output_file):
    """Retrieve the repository config locally"""
    repo_config = repo.describe()
    utils.serialize_yaml(repo_config, output_file)
    LOG.info("%s updated", output_file)


def _push_repo(repo, input_file):
    """Update the repository config in github"""
    new_config = utils.load_yaml(input_file)
    current_config = repo.describe()
    if utils.confirm_changes(current_config, new_config, abort=True):
        repo.update(new_config)


def _pull_org(org, output_file):
    """Retrieve the organization config locally"""
    org_config = org.describe()
    utils.serialize_yaml(org_config, output_file)
    LOG.info("%s updated", output_file)


def _push_org(org, input_file):
    """Update the organization config in github"""
    new_config = utils.load_yaml(input_file)
    current_config = org.describe()
    if utils.confirm_changes(current_config, new_config, abort=True):
        org.update(new_config)


def _update_all_repos(gh, org, input_file, repo_filter=None):
    """Updates all repos of an org with the specified repo config

    This will iterate over all repos in the org and update them with the template provided
    "Repo specific fields" will be ignored if presents in the repo file

    If a repo filter is provided the name of the repo have to match with that
    """
    ignored_options = ["name", "description", "homepage"]

    new_config = utils.load_yaml(input_file)
    if any(_ in new_config["options"] for _ in ignored_options):
        message = ("{} keys wont be updated but they are present in {}.\n"
                   "Continue anyway?".format(ignored_options, input_file))
        click.confirm(message, abort=True, default=True)

    for field in ignored_options:
        new_config["options"].pop(field, None)

    for repo_name in org.repos:
        if repo_filter and not fnmatch.fnmatch(repo_name, repo_filter):
            LOG.info("Skipping '{}/{}'".format(org.name, repo_name))
            continue
        LOG.info("Updating %s", repo_name)
        r = Repo(gh, org.name, repo_name)
        current_config = r.describe()
        for field in set(ignored_options) - {"name"}:
            current_config["options"].pop(field, None)
        new_config["options"]["name"] = repo_name
        if utils.confirm_changes(current_config, new_config):
            r.update(new_config)

    LOG.info("All repos in %s processed", org.name)


# OLD DEPRECATED FUNCTIONS

@dothub.group()
@click.option("--owner", help="GitHub owner of the repo", required=False)
@click.option("--repository", help="GitHub repo to serialize", required=False)
@click.pass_context
def repo(ctx, owner, repository):
    """Serialize/Update the repository config. Deprecated, prefer push/pull"""
    ws_repo_info = utils.workspace_repo()
    if ws_repo_info:
        ws_owner, ws_repo = ws_repo_info
        owner = owner or ws_owner
        repository = repository or ws_repo
    if not owner:
        raise click.BadArgumentUsage(
            "Either provide an owner or run this within a repo",
            ctx=ctx
        )
    if not repository:
        raise click.BadArgumentUsage(
            "Either provide a repo or run this within a repo",
            ctx=ctx
        )

    gh = ctx.obj['github']
    ctx.obj['repository'] = Repo(gh, owner, repository)


@repo.command("pull")
@click.option("--output_file", help="Output config file", default=REPO_CONFIG_FILE)
@click.pass_context
def repo_pull(ctx, output_file):
    """Retrieve the repository config locally"""
    _pull_repo(ctx.obj["repository"], output_file)


@repo.command("push")
@click.option("--input_file", help="Input config file", default=REPO_CONFIG_FILE)
@click.pass_context
def repo_push(ctx, input_file):
    """Update the repository config in github"""
    _push_repo(ctx.obj["repository"], input_file)


@dothub.group()
@click.option("--name", help="GitHub organization name", required=False)
@click.pass_context
def org(ctx, name):
    """Serialize/Update the org config. Deprecated, prefer push/pull"""
    ws_repo_info = utils.workspace_repo()
    if ws_repo_info:
        ws_owner, ws_repo = ws_repo_info
        name = name or ws_owner
    gh = ctx.obj['github']
    ctx.obj['organization'] = Organization(gh, name)


@org.command("pull")
@click.option("--output_file", help="Output config file", default=ORG_CONFIG_FILE)
@click.pass_context
def org_pull(ctx, output_file):
    """Retrieve the organization config locally"""
    _pull_org(ctx.obj['organization'], output_file)


@org.command("push")
@click.option("--input_file", help="Input config file", default=ORG_CONFIG_FILE)
@click.pass_context
def org_push(ctx, input_file):
    """Update the organization config in github"""
    _push_org(ctx.obj['organization'], input_file)


@org.command()
@click.option("--input_file", help="Input config file", default=ORG_REPOS_CONFIG_FILE)
@click.pass_context
def repos(ctx, input_file):
    """Updates all repos of an org with the specified repo config

    This will iterate over all repos in the org and update them with the template provided
    "Repo specific fields" will be ignored if presents in the repo file
    """
    gh = ctx.obj['github']
    o = ctx.obj['organization']
    new_config = utils.load_yaml(input_file)
    _update_all_repos(gh, o, new_config)
