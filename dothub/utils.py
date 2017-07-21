"""Some common utils"""
import logging
import yaml
import git
import re
from deepdiff import DeepDiff
from six import string_types
import click

from yaml import Loader, SafeLoader

LOG = logging.getLogger(__name__)


def construct_yaml_str(self, node):
    # Override the default string handling function
    # to always return unicode objects
    return self.construct_scalar(node)
Loader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)


def decode_permissions(permissions_dict):
    """Given a permissions dict, returns the highest permission"""
    if permissions_dict.get("admin"):
        return "admin"
    elif permissions_dict.get("push"):
        return "push"
    elif permissions_dict.get("pull"):
        return "pull"
    else:
        raise ValueError("Unexpected permission options: {}"
                         .format(permissions_dict))


def serialize_yaml(config, file_name=None):
    """Serialzes the yaml, returns if no file_name passed in"""
    f = open(file_name, 'w') if file_name else None
    return yaml.safe_dump(config, f, encoding='utf-8', allow_unicode=True,
                          default_flow_style=False)


def load_yaml(file_name):
    with open(file_name) as f:
        return yaml.safe_load(f)


def extract_gh_info_from_uri(input_uri):
    """Given a valid github uri extracts the owner and the repo"""
    return re.search(r".*[:/]([^/]+)/(.*)\.git", input_uri).groups()


def workspace_repo():
    """Extracts the owner and repository of the current workspace
    return a tuple as (owner, repo)
    """
    try:
        ws_repo = git.Repo()
        tracking_branch = ws_repo.active_branch.tracking_branch()
        tracking_remote = tracking_branch.remote_name if tracking_branch else "origin"
        remote = [r for r in ws_repo.remotes if r.name == tracking_remote][0]
        return extract_gh_info_from_uri(list(remote.urls)[0])
    except (git.exc.InvalidGitRepositoryError, IndexError, AttributeError,
            ValueError, TypeError):
        return None


def confirm_changes(current, new, abort=False):
    """Prints the proposed changes and asks for confirmation

    Keys present in current but missing in new are considered unchanged

    :param current: Current config to compare with
    :param new: new changes to apply
    :param abort: abort app if the user rejects changes (return false otherwise)
    :return: True if the user wants the changes, False if there are no changes or rejected
    """
    added, removed, changed = diff_configs(current, new)
    if not(added or removed or changed):
        return False

    LOG.info("Changes: ")

    for l in added:
        LOG.info(click.style("+ {}".format(l), fg='green'))
    for l in removed:
        LOG.info(click.style("- {}".format(l), fg='red'))
    for l, v in changed.items():
        LOG.info(click.style("C {0} ({1[old_value]} -> {1[new_value]})".format(l, v), fg='yellow'))

    return click.confirm("Apply changes?", abort=abort, default=True)


def diff_configs(current, new):
    """Diffs to dict using DeepDiff and returning the changes ready to print

    Keys present in current but missing in new are considered unchanged

    Returns a tuple of added, removed and updated
    """
    current = {k: current[k] for k in new}
    d = DeepDiff(current, new, ignore_order=True)
    added = set()
    removed = set()
    changed = d.get("values_changed", dict())
    for key_change, change in d.get("type_changes", dict()).items():
        if change["new_value"] == change["old_value"]: # str vs unicode type changes
            continue
        else:
            changed[key_change] = change
    for key in ["dictionary_item_added", "iterable_item_added", "attribute_added",
                "set_item_added"]:
        added = added.union(d.get(key, set()))
    for key in ["dictionary_item_removed", "iterable_item_removed", "attribute_removed",
                "set_item_removed"]:
        removed = removed.union(d.get(key, set()))
    return added, removed, changed
