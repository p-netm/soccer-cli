import os
import sys
sys.path.append('soccer')
import json
import requests
import unittest
from  unittest.mock import Mock, patch


from soccer.request_handler import RequestHandler, APIErrorException


@patch('requests.get')
class TestRequestHandler(unittest.TestCase):
    def setUp(self):
        dummy_key = 12345678901234567890123456789012
        self.headers = {'X-Auth-Token': dummy_key}
        url = 'http://api.football-data.org/v2/'
        self.dummy_url = url
        self.rq = RequestHandler()

    def tearDown(self):
        pass

    def test_ok_code(self, mock_get):
        res = {
            'data': 'data'
        }
        mock_get.return_value = Mock(status_code=requests.codes.ok)
        mock_get.return_value.json.return_value = res
        try:
            self.rq.get(self.dummy_url, headers=self.headers)
        except APIErrorException:
            self.fail("Threw exception erroneously")

    def test_bad_code(self, mock_get):
        res = {
            'error': requests.codes.bad,
            'message': 'Bad Request'
        }
        mock_get.return_value = Mock(status_code=requests.codes.bad)
        mock_get.return_value.json.return_value = res

        with self.assertRaises(APIErrorException) as context:
            self.rq.get(self.dummy_url, headers=self.headers)

        self.assertIn('Bad Request', context.exception.__str__())

    def test_forbidden_code(self, mock_get):
        res = {
            'error': requests.codes.forbidden,
            'message': 'Disallowed request'
        }
        mock_get.return_value = Mock(status_code=requests.codes.forbidden)
        mock_get.return_value.json.return_value = res
        with self.assertRaises(APIErrorException) as context:
            self.rq.get(self.dummy_url, headers=self.headers)
            import pdb; pdb.set_trace()

        self.assertTrue('This resource is restricted' in context.exception.__str__())
        self.assertTrue("Disallowed request" in context.exception.__str__())

    def test_not_found_code(self, mock_get):
        res = {
            'error': requests.codes.not_found,
            'message': 'Page not found'
        }
        mock_get.return_value = Mock(status_code=requests.codes.not_found)
        mock_get.return_value.json.return_value = res
        with self.assertRaises(APIErrorException) as context:
            self.rq.get(self.dummy_url, headers=self.headers)

        self.assertTrue("This resource does not exist. "
                            "Check parameters" in context.exception.__str__())
        self.assertTrue("Page not found" in context.exception.__str__())

    def test_too_many_requests_code(self, mock_get):
        res = {
            'error': requests.codes.too_many_requests,
            'message': 'Quota excedeed'
        }
        mock_get.return_value = Mock(status_code=requests.codes.too_many_requests)
        mock_get.return_value.json.return_value = res
        with self.assertRaises(APIErrorException) as context:
            self.rq._get(self.dummy_url, headers=self.headers)

        self.assertTrue("You have exceeded your allowed "
                            "requests per minute/day" in context.exception.__str__())
        self.assertTrue('Quota excedeed' in context.exception.__str__())


if __name__ == '__main__':
    unittest.main()
