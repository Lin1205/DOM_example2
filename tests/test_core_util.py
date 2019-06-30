#
#
#   test_core_util.py
#   ~~~~~~~~~~~~~~~~~
#
#   Test module for core.util
#
import unittest

import core.util as cu

class TestUtil(unittest.TestCase):

    base_config_path = '../config/scraper_config.yml'

    def test_util_load_scraper_config(self):
        """ Confirm that injested config contains 'db_path' """

        config_in = cu.load_config(self.base_config_path)

        self.assertTrue('db_path' in config_in.keys())