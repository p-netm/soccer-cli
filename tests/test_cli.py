"""GENERAL GOAL
see if request is called with the required url string
after aggregating the user input from the cli
"""
from click.testing import CliRunner
from click import Abort as abort
import unittest
from unittest.mock import patch, Mock
from soccer.main import main


@patch('soccer.writers.Stdout')  # mock_writer; role?
@patch('soccer.request_handler.RequestHandler._get')
class cliTest(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass

    def test_cli_entry(self, mock_get, mock_writer):
        result = self.runner.invoke(main, ['--help'])
        self.assertEqual(0, result.exit_code)
        self.assertIn('A CLI for live and past football scores from various football leagues',
                      result.output)

    def default_check(self, result, mock_get, mock_writer):
        self.assertEqual(0, result.exit_code)
        self.assertTrue(mock_get.called)

    def test_competition_resource(self, mock_get, mock_writer):
        result = self.runner.invoke(main, ['competitions', '--help'])
        self.assertTrue('Competitions Resource Endpoint' in result.output)

    @unittest.skip('Looking into implementing this in next iteration')
    def test_competitions_resource_alias(self, mock_get, mock_writer):
        """leagues should be an alias for competitoins and should provide an interface to the whole
        arsenam od options and commands under competitions"""
        result = self.runner.invoke(main, ['leagues', '--help'])
        self.assertTrue('Competitions Resource Endpoint' in result.output)

    # test competitions subresources
    def test_competitions_sub_resources_invoction_without_competitions_id(self, mock_get, mock_writer):

        res = self.runner.invoke(main, 'competitions standings'.split())
        res1 = self.runner.invoke(main, 'competitions matches'.split())
        res2 = self.runner.invoke(main, 'competitions scorers'.split())
        res3 = self.runner.invoke(main, 'competitions teams'.split())
        for result in [res, res1, res2, res3]:
            self.assertIn('Aborted', result.output)

    def test_standings_subresource(self, mock_get, mock_writer):
        result = self.runner.invoke(main, 'competitions -i 2021 standings --help'.split())
        self.assertTrue('Standings subresource for the competitions resource' in result.output)
        result = self.runner.invoke(main, 'competitions -i 2021 standings --standingtype home'.split())
        self.default_check(result, mock_get, mock_writer)

    def test_scorers_subresource(self, mock_get, mock_writer):
        result = self.runner.invoke(main, 'competitions -i 2021 scorers --help'.split())
        self.assertTrue('Scorers subresource for competitions resource' in result.output)
        result = self.runner.invoke(main, 'competitions -i 2021 scorers -l 20'.split())
        self.default_check(result, mock_get, mock_writer)

    def test_teams_subresources(self, mock_get, mock_writer):
        result = self.runner.invoke(main, 'competitions -i 2021 teams --help'.split())
        self.assertTrue('Subresource for teams within competitions' in result.output)
        # filters
        result = self.runner.invoke(main, 'competitions -i 2021 teams --season 2017 --stage REGULAR_SEASON'.split())
        self.default_check(result, mock_get, mock_writer)

    def test_matches_subresources(self, mock_get, mock_writer):
        result = self.runner.invoke(main, 'competitions -i 2021 matches --help'.split())
        self.assertTrue('subresource of matches within competitions' in result.output)

        # check filters
        query = 'competitions -i 2021 matches -f 2018-10-10 -t 2018-10-11 --status finished' \
                ' --matchday 2 --season 2017 --stage GROUP_STAGE --group A'
        result = self.runner.invoke(main, query.split())
        self.default_check(result, mock_get, mock_writer)

    def test_competition_filters(self, mock_get, mock_writer):
        result = self.runner.invoke(main, ['competitions', '--areas', '2072',  '--plan', 'TIER_ONE'])
        self.default_check(result, mock_get, mock_writer)

    def test_matches_resource(self, mock_get, mock_writer):  # skipped matches
        result = self.runner.invoke(main, 'matches --help'.split())
        self.assertTrue('Matches Resource Endpoint' in result.output)

    def test_matches_resource_filters(self, mock_get, mock_writer):
        result = self.runner.invoke(main, 'matches -f 2018-10-10 -t 2018-10-11 -c 2000 -s finished'.split())
        self.default_check(result, mock_get, mock_writer)

    def test_players_resource(self, mock_get, mock_writer):
        # first check the help, single player and all players
        result = self.runner.invoke(main, 'players --help'.split())
        self.assertIn("Players Resource Endpoint", result.output)
        result = self.runner.invoke(main, ['players'])
        self.assertIn('Aborted', result.output)
        result = self.runner.invoke(main, 'players -c 2021'.split())
        self.assertIn('Aborted', result.output)

    def test_players_resource_filters(self, mock_get, mock_writer):
        result = self.runner.invoke(main,
                                    'players -i 1 -m -f 2018-10-10 -t 2018-10-11 -c 2000 -c 2011 -s finished -l 20'.split())
        self.default_check(result, mock_get, mock_writer)

    def test_areas_resource(self, mock_get, mock_writer):
        result = self.runner.invoke(main, 'areas --help'.split())
        self.assertTrue('Areas Resource Endpoint' in result.output)
        result = self.runner.invoke(main, ['areas'])
        result1 = self.runner.invoke(main, 'areas -i 2072')
        self.default_check(result, mock_get, mock_writer)
        self.default_check(result1, mock_get, mock_writer)

    def test_teams_resource_general(self, mock_get, mock_writer):
        result = self.runner.invoke(main, 'teams --help'.split())
        self.assertIn('Teams Resource Endpoint', result.output)

        result = self.runner.invoke(main, 'teams --venue home'.split())
        self.assertEqual(0, result.exit_code)
        self.assertIn('Aborted', result.output)

    def test_teams_resource_with_filters(self, mock_get, mock_writer):
        result = self.runner.invoke(main, 'teams -i 57 -m -f 2018-10-10 -t 2018-10-11 -v away -s finished -l 20'.split())
        self.default_check(result, mock_get, mock_writer)

# pending cli tests: output file and mode, listcodes