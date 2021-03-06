from requests import ConnectionError
from urllib.parse import urljoin as join
import requests
import click

try:
    from soccer.exceptions import APIErrorException
except ImportError as error:
    from exceptions import APIErrorException


class RequestHandler(object):

    BASE_URL = 'http://api.football-data.org/v2/'

    def __init__(self, writer=None):
        self.writer = writer

    def _get(self, url, **kwargs):
        """Handles api.football-data.org requests"""
        url = join(RequestHandler.BASE_URL,url)
        req = requests.get(url, **kwargs)

        if req.status_code == requests.codes.ok:
            return req.json()

        if req.status_code == requests.codes.bad:
            raise APIErrorException('Invalid request. Check parameters; {}'.format(req.json().get('message')))

        if req.status_code == requests.codes.forbidden:
            raise APIErrorException('This resource is restricted; {}'.format(req.json().get('message')))

        if req.status_code == requests.codes.not_found:
            raise APIErrorException('This resource does not exist. Check parameters; {}'.format(req.json().get('message')))

        if req.status_code == requests.codes.too_many_requests:
            raise APIErrorException('You have exceeded your allowed requests per minute/day; {}'. format(req.json().get('message')))

        if req.status_code == 500:
            raise APIErrorException('This has nothing to do with you. {}'.format(req.json()['message']))
