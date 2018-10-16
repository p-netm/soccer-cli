import unittest
import random
from soccer.validators import validate_competitions, validate_date, validate_plan, validate_limit, \
    validate_matchday, validate_season, validate_status, validate_venue, validate_standing


class ValidatorTest(unittest.TestCase):

    def test_all_for_validators_for_valid_data(self):
        # test validate match
        res = validate_matchday(None, None, '13')
        res2 = validate_matchday(None, None, '109')
        res3 = validate_matchday(None, None, '1')
        self.assertEqual(13, res)
        self.assertEqual(109, res2)
        self.assertEqual(1, res3)

        # test valid_season
        season_res = validate_season(None, None, '1850')
        self.assertTrue('1850', season_res)

        # test_validate_status
        sample = ['SCHEDULED', 'LIVE', 'IN_PLAY', 'PAUSED', 'FINISHED', 'POSTPONED', 'SUSPENDED', 'CANCELED', 'AWARDED']
        inp = random.choice(sample)
        if random.randint(0,1):
            inp = inp.lower()
        self.assertEqual(inp.upper, validate_standing(None, None, inp))

        # validate_venue
        self.assertEqual('HOME', validate_venue(None, None, 'home'))
        self.assertEqual('AWAY', validate_venue(None, None, 'away'))

        # validate_Date
        sample = '2018-12-22'
        self.assertEqual(sample, validate_date(None, None, sample))

        #validate_plan
        sample = ['TIER_ONE', 'TIER_TWO', 'TIER_THREE', 'TIER_FOUR']
        inp = random.choice(sample)
        if random.randint(0, 1): inp = inp.lower()
        self.assertEqual(inp.upper, validate_plan(None, None, inp))

        # validate competitions
        sample = ['1']
        sample2 = ['1', '2']
        self.assertEqual(sample, validate_competitions(None, None, sample))
        self.assertEqual(sample2, validate_competitions(None, None, sample2))

        # validate_limit
        self.assertEqual(5, validate_limit(None, None, '5'))

        #validate_standing
        self.assertEqual('TOTAL', validate_standing(None, None, 'total'))
