"""Some common utils"""
import yaml
import git
import re


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


def serialize_yaml(config, file_name):
    with open(file_name, 'w') as f:
        yaml.safe_dump(config, f, encoding='utf-8', allow_unicode=True,
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
        tracking_remote = ws_repo.active_branch.tracking_branch().remote_name
        remote = [r for r in ws_repo.remotes if r.name == tracking_remote][0]
        return extract_gh_info_from_uri(list(remote.urls)[0])
    except (git.exc.InvalidGitRepositoryError, IndexError, AttributeError,
            ValueError, TypeError):
        return None
