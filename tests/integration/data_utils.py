"""Utilities with the data for the tests"""
import os
import json
import copy


DATA_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_data_file(file_name):
    """Loads a data file from the data directory"""
    with open(os.path.join(DATA_FOLDER_PATH, file_name)) as data_file:
        return json.load(data_file)

REPO_DATA = load_data_file("repo_data.json")
ORG_DATA = load_data_file("org_data.json")

REPO_AND_ORG_DATA = copy.deepcopy(REPO_DATA)
REPO_AND_ORG_DATA.update(ORG_DATA)
