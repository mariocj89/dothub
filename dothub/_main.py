import click
import json
import os.path
import time
import getpass
import github_token
from dothub import utils
from dothub import github_helper
from dothub.repository import Repo
from dothub.organization import Organization


APP_DIR = click.get_app_dir("dothub")
CONFIG_FILE = os.path.join(APP_DIR, "config.json")
DEFAULT_API_URL = "https://api.github.com"
REPO_CONFIG_FILE = ".dothub.repo.yml"
ORG_CONFIG_FILE = ".dothub.org.yml"


def load_config():
    """Returns a config object loaded from disk or an empty dict"""
    try:
        with open(CONFIG_FILE) as f:
            conf = json.load(f)
    except IOError:
        conf = dict()
        conf["metadata"] = dict(config_time=time.time())
        if not os.path.isdir(APP_DIR):
            os.mkdir(APP_DIR)
        click.echo("Seems this is the first time you run dothub, let me configure your settings...")
        initial_config(conf)
        with open(CONFIG_FILE, 'w') as f:
            conf = json.dump(conf, f)
        click.echo("Config saved in: '{}'".format(CONFIG_FILE))
        click.echo("Delete this file to rerun the wizard")
    return conf


def initial_config(conf):
    """Asks the user for the general configuration for the app and fills the config object"""
    user = click.prompt("What is your username? ")
    password = getpass.getpass()
    token_factory = github_token.TokenFactory(user, password, "gitorg", github_token.ALL_SCOPES)
    token = token_factory(tfa_token_callback=lambda: click.prompt("Insert your TFA token: "))
    conf["token"] = token
    github_url = click.prompt("What is your github instance API url? ", default=DEFAULT_API_URL)
    conf["github_base_url"] = github_url


@click.group()
@click.option("--user", help="GitHub user to use", envvar="GITHUB_USER", required=True)
@click.option("--token", help="GitHub API token to use", envvar="GITHUB_TOKEN", required=True)
@click.option("--github_base_url", help="GitHub base api url",
              envvar="GITHUB_API_URL", default=DEFAULT_API_URL)
@click.pass_context
def dothub(ctx, user, token, github_base_url):
    """Configure github as code!

    Stop using the keyboard like a mere human and store your github config in a file"""
    gh = github_helper.GitHub(user, token, github_base_url)
    ctx.obj['github'] = gh


@dothub.group()
@click.option("--organization", help="GitHub organization of the repo", required=True)
@click.option("--repository", help="GitHub repo to serialize", required=True)
@click.pass_context
def repo(ctx, organization, repository):
    """Serialize/Update the repository config"""
    gh = ctx.obj['github']
    ctx.obj['repository'] = Repo(gh, organization, repository)


@repo.command("pull")
@click.option("--output_file", help="Output config file", default=REPO_CONFIG_FILE)
@click.pass_context
def repo_pull(ctx, output_file):
    """Retrieve the repository config locally"""
    r = ctx.obj['repository']
    repo_config = r.describe()
    utils.serialize_yaml(repo_config, output_file)


@repo.command("push")
@click.option("--input_file", help="Input config file", default=REPO_CONFIG_FILE)
@click.pass_context
def repo_push(ctx, input_file):
    """Update the repository config in github"""
    r = ctx.obj['repository']
    config = utils.load_yaml(input_file)
    r.update(config)


@dothub.group()
@click.option("--name", help="GitHub organization name", required=True)
@click.pass_context
def org(ctx, name):
    """Serialize/Update the org config"""
    gh = ctx.obj['github']
    ctx.obj['organization'] = Organization(gh, name)


@org.command("pull")
@click.option("--output_file", help="Output config file", default=ORG_CONFIG_FILE)
@click.pass_context
def org_pull(ctx, output_file):
    """Retrieve the organization config locally"""
    o = ctx.obj['organization']
    org_config = o.describe()
    utils.serialize_yaml(org_config, output_file)


@org.command("push")
@click.option("--input_file", help="Input config file", default=ORG_CONFIG_FILE)
@click.pass_context
def org_push(ctx, input_file):
    """Update the organization config in github"""
    o = ctx.obj['organization']
    config = utils.load_yaml(input_file)
    o.update(config)
