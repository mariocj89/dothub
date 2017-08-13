"""Utilities with the data for the tests"""
from __future__ import unicode_literals
import os
import json
import copy
import sealedmock
import base64


DATA_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_data_file(file_name):
    """Loads a data file from the data directory"""
    with open(os.path.join(DATA_FOLDER_PATH, file_name)) as data_file:
        return json.load(data_file)

REPO_DATA = load_data_file("repo_data.json")
ORG_DATA = load_data_file("org_data.json")


def requests_mock(payloads):
    def _(url):
        """Using the urls in payloads builds a mock and returns it"""
        res_payload = payloads[url]
        mock = sealedmock.SealedMock()
        mock.text = json.dumps(res_payload)
        mock.json.return_value = copy.deepcopy(res_payload)
        mock.raise_for_status = lambda: None
        mock.sealed = True
        return mock
    return _


# Config based on the configuration file
DOTHUB_REPO_CONFIG = {
    "hooks": {
        "travis": {
            "active": False,
            "config": {
                "domain": "notify.travis-ci.org",
                "token": "********",
                "user": "mariocj89"
            },
            "events": [
                "issue_comment",
                "member",
                "public",
                "pull_request",
                "push"
            ]
        }
    },
    "collaborators": {
        "mariocj89": {
            "permission": "admin"
        }
    },
    "labels": {
        "question": {
            "color": "cc317c"
        },
        "invalid": {
            "color": "e6e6e6"
        },
        "duplicate": {
            "color": "cccccc"
        },
        "help wanted": {
            "color": "159818"
        },
        "wontfix": {
            "color": "ffffff"
        },
        "bug": {
            "color": "fc2929"
        },
        "enhancement": {
            "color": "84b6eb"
        }
    },
    "options": {
        "has_wiki": True,
        "homepage": "",
        "description": None,
        "has_downloads": True,
        "private": False,
        "has_issues": False,
        "name": "echaloasuerte"
    }
}

DOTHUB_ORG_CONFIG = {
    "hooks": {},
    "options": {
        "billing_email": "mariocj89@gmail.com",
        "location": "",
        "email": "",
        "description": "Group of friends that code :)",
        "company": None,
        "name": "EtCaterva"
    },
    "members": {
        "dnaranjo89": {
            "role": "admin"
        },
        "palvarez89": {
            "role": "admin"
        },
        "mariocj89": {
            "role": "admin"
        }
    },
    "teams": {
        "Mobile": {
            "description": "Pepole working in the apps",
            "permission": "pull",
            "privacy": "closed",
            "repositories": {
                "echaloasuerte-mobile": {
                    "permission": "pull"
                },
                "deployment": {
                    "permission": "pull"
                }
            },
            "id": 1827619,
            "members": {
                "mariocj89": {
                    "role": "member"
                }
            }
        },
        "Web": {
            "description": "Web developers",
            "permission": "pull",
            "privacy": "closed",
            "repositories": {
                "echaloasuerte-legacy": {
                    "permission": "push"
                },
                "echaloasuerte": {
                    "permission": "push"
                },
                "etcaterva-web": {
                    "permission": "push"
                }
            },
            "id": 1827620,
            "members": {
                "dnaranjo89": {
                    "role": "member"
                },
                "mariocj89": {
                    "role": "member"
                }
            }
        },
        "Automation": {
            "description": "",
            "permission": "admin",
            "privacy": "closed",
            "repositories": {
                "deployment": {
                    "permission": "push"
                }
            },
            "id": 1338338,
            "members": {
                "palvarez89": {
                    "role": "member"
                },
                "mariocj89": {
                    "role": "member"
                }
            }
        }
    }
}

REPO_DATA[".*contents/.dothub.repo.yml"]["content"] = base64.b64encode(json.dumps(DOTHUB_REPO_CONFIG, ensure_ascii=False).encode())
REPO_DATA[".*contents/.dothub.org.yml"]["content"] = base64.b64encode(json.dumps(DOTHUB_ORG_CONFIG, ensure_ascii=False).encode())

REPO_AND_ORG_DATA = copy.deepcopy(REPO_DATA)
REPO_AND_ORG_DATA.update(ORG_DATA)


