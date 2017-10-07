"""Helper to retrieve/push data from/to github"""
import logging
import requests
from requests.compat import urljoin

DEFAULT_API_URL = "https://api.github.com"
LOG = logging.getLogger(__name__)


def _mask_dict(in_dict, mask):
    """Given a dict and a list of fields removes all fields not in the list"""
    for key in (set(in_dict.keys()) - set(mask)):
        in_dict.pop(key)
    return in_dict


class GitHub(object):
    """Handle to send HTTP requests to github

    It basically adds authentication, github as base url and field masking
    on top of Python requests.
    """

    # Single global ugly horrible session to ease testing
    # set this value to any kind of mock  and it will be used
    # instead of an instance of requests.Session
    _session = None

    def __init__(self, user, token, api_url=DEFAULT_API_URL):
        """Creates a repo object

        :param user: user to authenticate
        :param token: token to use for authentication. It can also be the user password
        """
        self.api_url = api_url
        self._session = self._session or requests.Session()
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
        result = self._request("get", url)
        if isinstance(result, dict):
            return _mask_dict(result, fields)
        elif isinstance(result, list):
            return [_mask_dict(item, fields)
                    for item in result]
        else:
            raise ValueError("Unexpected type from github: {}"
                             .format(repr(result)))

    def put(self, url, payload):
        """Sends a put to the url

        :param url: url to put (within the github api). Ex: /repos/mario/repo1/tags
        :type url: str
        :param payload: the payload to send
        :type payload: dict
        """
        return self._request("put", url, json=payload)

    def patch(self, url, payload):
        """Sends a patch to the url

        :param url: url to patch (within the github api). Ex: /repos/mario/repo1/tags
        :type url: str
        :param payload: the payload to send
        :type payload: dict
        """
        return self._request("patch", url, json=payload)

    def post(self, url, payload):
        """Sends a post to the url

        :param url: url to post (within the github api). Ex: /repos/mario/repo1/tags
        :type url: str
        :param payload: the payload to send
        :type payload: dict
        """
        return self._request("post", url, json=payload)

    def delete(self, url):
        """Sends a delete to the url

        :param url: url to delete (within the github api). Ex: /repos/mario/repo1/tags
        :type url: str
        """
        self._request("delete", url)

    def _request(self, method, url, **kwargs):
        """Shared plumbing to send a request"""
        req_func = getattr(self._session, method)
        try:
            response = req_func(urljoin(self.api_url, url), **kwargs)
            response.raise_for_status()
        except:
            LOG.debug("Failed to send %s request to %s", method, url, exc_info=True)
            raise
        else:
            LOG.debug("Request to '%s' returned %s", url, response.text)
        if response.text:
            return response.json()

