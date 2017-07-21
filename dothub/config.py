import getpass
import json
import time
import os
import logging

import click
import github_token
import os.path


DEFAULT_API_URL = "https://api.github.com"
APP_DIR = click.get_app_dir("dothub")
CONFIG_FILE = os.path.join(APP_DIR, "config.json")
AUTO_CONFIG = {}
LOG = logging.getLogger(__name__)


def load_config():
    """Returns a config object loaded from disk or an empty dict"""
    try:
        with open(CONFIG_FILE) as f:
            conf = json.load(f)
    except IOError:
        if os.environ.get("GITHUB_USER") and os.environ.get("GITHUB_TOKEN"):
            conf = AUTO_CONFIG
        else:
            LOG.info("Seems this is the first time you run dothub,"
                     " let me configure your settings...")
            conf = config_wizard()
    return conf


def config_wizard():
    """Runs the config wizard to configure all defaults for the application"""
    conf = dict()
    conf["metadata"] = dict(config_time=time.time())
    if not os.path.isdir(APP_DIR):
        os.makedirs(APP_DIR)
    initial_config(conf)
    with open(CONFIG_FILE, 'w') as f:
        conf = json.dump(conf, f, indent=4)
    LOG.info("Config saved in: '{}'".format(CONFIG_FILE))
    LOG.info("Delete this file to rerun the wizard")
    return conf


def initial_config(conf):
    """Asks the user for the general configuration for the app and fills the config object"""
    user = click.prompt("What is your username? ")
    conf["user"] = user
    password = getpass.getpass()
    token_factory = github_token.TokenFactory(user, password, "gitorg", github_token.ALL_SCOPES)
    token = token_factory(tfa_token_callback=lambda: click.prompt("Insert your TFA token: "))
    conf["token"] = token
    github_url = click.prompt("What is your github instance API url? ", default=DEFAULT_API_URL)
    conf["github_base_url"] = github_url
