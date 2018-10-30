"""
Goal: Check that we have at least certain expected texts in the returned responses
and that the functions in charge of returning the above said response run as expected
"""

from unittest.mock import Mock, patch
import unittest, json, os
from soccer.writers import Stdout, Json
from .sample_data import data
from datetime import datetime


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

    def test_competition_for_single_competition(self, mecho):
        comp = data['single_competition']
        self.writer.write_competition(comp)
        self.assertTrue(mecho.called)
        self.assertEqual(mecho.call_count, 1)

    def test_above_with_the_full_argument(self, mecho):
        comp = data['single_competition']
        self.writer.write_competition(comp, full=True)
        self.assertTrue(mecho.call_count > 23 )

    def test_write_competitions_for_single_competition(self, mecho):
        comp = data['single_competition']
        self.writer.write_competitions(comp)
        self.assertTrue(mecho.called)

    def test_write_scorers(self, mecho):
        scorers = data['many_scorers']
        self.writer.write_scorers(scorers)
        self.assertTrue(mecho.call_count > 10)

    def test_aggregate_match_data(self, mecho):
        response = self.writer.aggregate_match_data([],[],[])
        self.assertListEqual(response, [])
        sample = [
            [
                {
                    'minute': 25,
                    'scorer': 'Christiano Ronaldo'
                }
            ],
            [
              {
                    'minute': 10,
                    'scorer': 'Antony Martial'
                }  
            ],
            [
                {
                    'minute': 5,
                    'scorer': 'Eden Hazard'
                },
                {
                    'minute': 56,
                    'scorer': 'Romelu Lukaku'
                }
            ]
        ]
        expected = [
            
                {
                    'minute': 5,
                    'scorer': 'Eden Hazard'
                },
            
              {
                    'minute': 10,
                    'scorer': 'Antony Martial'
                } ,  
            
                {
                    'minute': 25,
                    'scorer': 'Christiano Ronaldo'
                },
                {
                    'minute': 56,
                    'scorer': 'Romelu Lukaku'
                }
            
        ]
        response = self.writer.aggregate_match_data(sample[0], sample[1], sample[2])
        self.assertListEqual(expected, response)

    def test_time_converter_for_standard_conversions(self, mecho):
        sample = "2018-08-10"
        sample2 = "2018-10-26T00:00:18Z"
        # test direct conversions
        self.assertEqual('03:00', Stdout.convert_utc_to_local_time(sample))
        response = Stdout.convert_utc_to_local_time(sample2)
        self.assertEqual('03:00', response)

    def test_time_converter_time_difference(self, mecho):
        """tests the time difference in years from the given date to today"""
        sample = "2018-08-10"
        sample2 = "2018-10-26T00:00:18Z"
        response = Stdout.convert_utc_to_local_time(sample, time_diff=True)
        response2 = Stdout.convert_utc_to_local_time(sample2, time_diff=True)
        self.assertIsInstance(response, int)
        self.assertIsInstance(response, int)

    def test_parse_season(self, mecho):
        start_date = "2018-08-10"
        end_date = "2019-05-12"
        expected = '2018/2019'
        response = Stdout.parse_season(start_date, end_date)
        response2 = Stdout.parse_season(end_date, start_date)
        self.assertEqual(response, expected)
        self.assertEqual(response2, expected)

    def test_write_standings(self, mecho):
        # Here we only check if the function terminates without any errors
        standings  = data['standings']
        self.writer.write_standings(standings)
        self.assertTrue(mecho.called)

    def test_write_group_Standings(self, mecho):
        # only check for the lack of syntax errors, does not check logical errors
        gstandings = data['group_standings']
        self.writer.write_standings(gstandings)
        self.assertTrue(mecho.called)

    def test_write_match_function(self, mecho):
        single_match = data['single_match']
        self.writer.write_match(single_match)
        self.assertEqual(mecho.called, 1)

    def test_write_match_with_fullness_argument(self, mecho):
        # a match record without the sub and bookings data
        single_match = data['single_match']
        self.writer.write_match(single_match, full=True)
        self.assertEqual(mecho.call_count, 2)
        # a match record with the full extra data
        mecho.reset()
        full_match = data['full_match']
        self.writer.write_match(full_match, full=True)
        self.assertTrue(mecho.called)

    def test_write_matches(self, mecho):
        many_matches = data['many_matches']
        single_match = data['single_match']
        self.writer.write_matches(single_match)
        self.assertEqual(mecho.call_count, 4)
        mecho.reset()
        self.writer.write_matches(many_matches)
        self.assertTrue(mecho.call_count > 6)    

if __name__ == '__main__':
    unittest.main()