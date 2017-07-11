"""Helper to retrieve/push data from/to github"""
import requests
from requests.compat import urljoin

DEFAULT_API_URL = "https://api.github.com"


def mask_dict(in_dict, mask):
    """Given a dict and a list of fields removes all fields not in the list"""
    for key in (set(in_dict.keys()) - set(mask)):
        in_dict.pop(key)
    return in_dict


class GitHub(object):
    """Represents an repository on github.

    It helps to retrieve the repository configuration and all of its
    elements
    """
    def __init__(self, user, token, api_url=DEFAULT_API_URL):
        """Creates a repo object

        :param user: user to authenticate
        :param token: token to use for authentication. It can also be the user password
        """
        self.api_url = api_url
        self._session = requests.Session()
        self._session.auth = (user, token)

    def get(self, url, fields):
        """Retrieves all fields from an url using a mask

        This helper function will get the json from the "sub url" provided
        and mask the result through the fields passed in.

        If the Github API returns a list of objects the mask will be applied to
        each of the objects

        :param url: url to get the fields from (within the github api). Ex: /repos/mario/repo1/tags
        :param fields: fields that we look for from the response,
        only those will be returned
        :raises: if anything goes wrong with the request
        :return: the same object/list that github returns but masked
        """
        response = self._session.get(urljoin(self.api_url, url))
        response.raise_for_status()
        result = response.json()
        if isinstance(result, dict):
            return mask_dict(result, fields)
        elif isinstance(result, list):
            return [mask_dict(item, fields)
                    for item in response.json()]
        else:
            raise ValueError("Unexpected type from github: {}"
                             .format(repr(response)))

    def put(self, url, payload):
        """Sends a put to the url

        :param url: url to put (within the github api). Ex: /repos/mario/repo1/tags
        :type url: str
        :param payload: the payload to send
        :type payload: dict
        """
        response = self._session.put(urljoin(self.api_url, url), json=payload)
        response.raise_for_status()
        if response.text:
            return response.json()

    def patch(self, url, payload):
        """Sends a patch to the url

        :param url: url to patch (within the github api). Ex: /repos/mario/repo1/tags
        :type url: str
        :param payload: the payload to send
        :type payload: dict
        """
        response = self._session.patch(urljoin(self.api_url, url), json=payload)
        response.raise_for_status()
        if response.text:
            return response.json()

    def post(self, url, payload):
        """Sends a post to the url

        :param url: url to post (within the github api). Ex: /repos/mario/repo1/tags
        :type url: str
        :param payload: the payload to send
        :type payload: dict
        """
        response = self._session.post(urljoin(self.api_url, url), json=payload)
        response.raise_for_status()
        if response.text:
            return response.json()

    def delete(self, url):
        """Sends a delete to the url

        :param url: url to delete (within the github api). Ex: /repos/mario/repo1/tags
        :type url: str
        """
        response = self._session.delete(urljoin(self.api_url, url))
        response.raise_for_status()
