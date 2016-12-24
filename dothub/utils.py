"""Some common utils"""
import yaml


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
