"""Goal: Check that we have at least certain expected texts in the returned responses
and that the functions in charge of returning the above said response run as expected
"""

from unittest.mock import Mock, patch
import unittest, json, os
from soccer.writers import Stdout, Json
from .sample_data import data


#  Testing click.secho output
@patch('click.secho')
class StdoutWriterTests(unittest.TestCase):
    """Basic Test format: check if code throws any errors or at least contains
    important pices of information in the call aruments"""
    def setUp(self):
        self.writer = Stdout(None)

    def tearDown(self):
        pass

    def test_single_area_write(self, mecho):
        single_area = data['single_area']
        self.writer.write_areas(single_area)
        self.assertTrue(mecho.called)

    def test_many_areas_writer(self, mecho):
        many_areas = data['many_areas']
        self.writer.write_areas(many_areas)
        self.assertTrue(mecho.called)

    def test_write_player(self, mecho):
        player =  data['single_player']
        self.writer.write_player(player)
        self.assertTrue(mecho.called)

    def test_write_team(self, mecho):
        # Test single team
        team = data['single_team']
        self.writer.write_team(team)
        self.assertTrue(mecho.called)
        self.assertEqual(mecho.call_count, 1)

    def test_write_single_team_with_fullness(self, mecho):
        team = data['single_team']
        self.writer.write_team(team, full=True)
        self.assertTrue(mecho.called)
        self.assertEqual(mecho.call_count, 33)

    def test_writer_many_teams_with_single_team_instance(self, mecho):
        team = data['single_team']
        self.writer.write_teams(team)
        self.assertEqual(mecho.call_count, 33)

    def test_writer_many_teams(self, mecho):
        # now for many teams
        teams = data['many_teams']
        self.writer.write_teams(teams)
        self.assertEqual(mecho.call_count, len(teams['teams']) + 1)



if __name__ == '__main__':
    unittest.main()