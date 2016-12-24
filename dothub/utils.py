"""Some common utils"""


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
