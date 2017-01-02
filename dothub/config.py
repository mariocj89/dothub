import getpass
import json
import time

import click
import github_token
import os.path
from dothub.cli import DEFAULT_API_URL


APP_DIR = click.get_app_dir("dothub")
CONFIG_FILE = os.path.join(APP_DIR, "config.json")


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
            conf = json.dump(conf, f, indent=4)
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