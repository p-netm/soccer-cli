"""GENERAL GOAL
see if request is called with the required url string
after aggregating the user input from the cli
"""
from click.testing import CliRunner
import unittest

class cliTest(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass

    # patch the request_handler
    def test_competition_resource(self):
        result = self.runner.invoke('competitions --id 2000')
        result = self.runner.invoke('competitions --areas 2072')
        result = self.runner.invoke('competitions --plan TIER_ONE')