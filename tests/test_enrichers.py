#
#
#   test_enrichers.py
#   ~~~~~~~~~~~~~~~~~
#
#   Test module for collectors.enrichers
#
import unittest

import collectors.enrichers as ce


class TestEnrichers(unittest.TestCase):

    lat = 37.8232347
    long = -122.237027

    def setUp(self):
        """ Initialize """

        self.poi = ce.PointOfInterest(self.lat, self.long)

    def test_census_geo(self):
        """ Test census geography lookup function"""

        # about_dat_lat = 37.8232347
        # about_dat_long = -122.237027

        # place = ce.census_geo(about_dat_lat, about_dat_long)

        place = ce.Place(self.lat, self.long)

        self.assertEqual(place.block_fips, '060014262002029', msg='Block lookup success')


    def test_places_get_restraunts(self):

        # poi = ce.points_of_interest(self.lat, self.long)

        n, r = self.poi.get_restaurants()

        self.assertEqual(n, 7)

        self.assertGreater(r, 4.0)

    def test_places_get_dive_bars(self):

        n, r = self.poi.get_bad_bars()

        self.assertGreater(n, 0)

    def test_places_get_yoga(self):
        """ Expecting something like 17 so safe assert value is ~10 """

        n, r = self.poi.get_yoga()

        self.assertGreater(10, 0)

    def test_get_neighborhood(self):
        """ Use midtown Sac to test neighborhood name get """

        poi = ce.PointOfInterest(38.5725121, -121.4857919)

        neigh_name_long, neigh_name_short = poi.get_neighborhood()

        self.assertEqual(neigh_name_long, "Midtown")

        self.assertEqual(neigh_name_short, "Midtown")
