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
        import pdb;pdb.set_trace()
        single_area = data['single_area']
        self.writer.write_areas(single_area)
        self.assertTrue(mecho.called)

    def test_many_areas_writer(self, mecho):
        many_areas = data['many_areas']
        self.writer.write_areas(many_areas)
        self.assertTrue(mecho.called)


if __name__ == '__main__':
    unittest.main()