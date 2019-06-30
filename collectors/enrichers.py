#
#   enrichers.py
#   ~~~~~~~~~~~~
#
#   Web-services to retrieve data given a lat long
#
import os
import json
import statistics
import urllib

import requests

from core.util import load_config

# Find the project root assuming we are one dir deep.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config/scraper_config.yml')
SECRET_PATH = os.path.join(PROJECT_ROOT, 'config/secret_config.yml')
SEARCH_RADIUS = 2000


class Place:
    """
    Class to provide census geography lookup from lat long

    """

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.block_fips = None
        self.county_fips = None
        self.county_name = None
        self.state_fips = None
        self.state_name = None

        self.census_geo(self.latitude, self.longitude)

        return

    def census_geo(self, lat, long):
        """
        Get the corresponding census geography from lat long

        Census geo from lat long https://geo.fcc.gov/api/census/#!/block/get_block_find

        :param lat:
        :param long:
        :return: (tract, block)
        """

        BASE_URL = 'https://geo.fcc.gov/api/census/block/find'
        FORMAT = 'json'

        payload = {'latitude': lat, 'longitude': long, 'showall': 'true', 'format': FORMAT}

        resp = requests.get(BASE_URL, params=payload)

        if resp.status_code == 200:
            resp_obj = json.loads(resp.text)

            self.block_fips = resp_obj['Block']['FIPS']
            self.county_fips = resp_obj['County']['FIPS']
            self.county_name = resp_obj['County']['name']
            self.state_fips = resp_obj['State']['FIPS']
            self.state_name = resp_obj['State']['code']

        return

    def acs_data(self, fips):
        """  Census data getter

        "B19013E_001E": {
            "label": "Estimate!!Median household income in the past 12 months (in 2017 inflation-adjusted dollars)",
            "concept": "MEDIAN HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2017 INFLATION-ADJUSTED DOLLARS) (NATIVE HAWAIIAN AND OTHER PACIFIC ISLANDER ALONE HOUSEHOLDER)",
            "predicateType": "int",
            "group": "B19013E",
            "limit": 0,
            "attributes": "B19013E_001M,B19013E_001MA,B19013E_001EA"
        },

        """

        raise NotImplementedError


class PointOfInterest:
    """
    Get places such as upscale restaurants, gas stations, near lat long

    API arguments can be overridden with kwargs, and price restriction can be removed with kwargs containing
    no_price_restriction = True

    """

    def __init__(self, latitude, longitude, radius=SEARCH_RADIUS, min_price=3, max_price=4, asset_id=None):
        self.base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius
        self.min_price = min_price
        self.max_price = max_price
        self.asset_id = asset_id

        # Retrieve Google API key from secrets file
        sec_config = load_config(SECRET_PATH)
        self.g_key = sec_config['google_key']

    def _get_keyword(self, keyword, **kwargs):
        """ Internal getter for Google places keyword api endpoint """

        payload = {'location': str(self.latitude) + ',' + str(self.longitude), 'radius': self.radius,
                   'keyword': keyword, 'minprice': self.min_price, 'maxprice': self.max_price,
                   'key': self.g_key}

        if kwargs != {}:


            for k, v in kwargs.items():

                payload[k] = v

        if ('no_price_restriction' in kwargs.keys()) and kwargs['no_price_restriction']:

            payload.pop('no_price_restriction')
            payload.pop('minprice')
            payload.pop('maxprice')

        resp = requests.get(self.base_url, params=payload)
        results_obj = json.loads(resp.text)
        results = results_obj['results']

        n_sites = len(results)

        ratings = [x['rating'] for x in results]

        if len(ratings) > 0:    # Defend against undefined median if no matches found
            median_rating = statistics.median(ratings)
        else:
            median_rating = 0

        return n_sites, median_rating

    def get_neighborhood(self):
        """
        Given a lat long or address get neighborhood

        https://maps.googleapis.com/maps/api/geocode/json?latlng=38.5725121,-121.4857919&neighborhood&key=YOUR_API_KEY

        We hope to get a payload like this within address_components:
            {
               "long_name" : "Midtown",
               "short_name" : "Midtown",
               "types" : [ "neighborhood", "political" ]
            },

        :return: (long, short) names of neighborhood or (None, None)
        """

        base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

        payload = {'latlng': str(self.latitude) + ',' + str(self.longitude), 'key': self.g_key}

        resp = requests.get(base_url, params=payload)
        results_obj = json.loads(resp.text)

        if results_obj['status'] == 'OK':

            for add_comps in results_obj['results']:

                for comp in add_comps['address_components']:

                    if "neighborhood" in comp['types']:

                        return comp["long_name"], comp["short_name"]

            # Good results, but no neighborhood present
            return '', ''

        else:

            raise Exception(results_obj['error_message'])

    def _get_distance_to_keyword(self, search_text, **kwargs):
        """
        Internal getter for distance to a location identified by string

        For example, distance to "Whole Foods"

        :param search_text:
        :param kwargs:
        :return:
        """
        pass

    def get_restaurants(self):
        """

        https: // developers.google.com / places / web - service / search  # PlaceSearchRequests
        https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=37.8232347,-122.237027&radius=2000&keyword=restaurant&minprice=3&key=YOUR_API_KEY

        It's important to use keyword not type in the payload because type seems to be restricted to first or primary,
        and misses some results

        """

        n_sites, median_rating = self._get_keyword('restaurant')

        return n_sites, median_rating

    def get_good_bars(self):
        """
        https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=37.8232347,-122.237027&radius=1500&keyword=bar&minprice=3&key=YOUR_API_KEY

        We define a dive bar based on price level.  Ratings appear to be pretty good.

        :return:
        """

        n_sites, median_rating = self._get_keyword('bar', minprice=3, maxprice=5)

        return n_sites, median_rating

    def get_bad_bars(self):
        """
        https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=37.8232347,-122.237027&radius=1500&keyword=bar&maxprice=1&key=YOUR_API_KEY

        We define a bad, dive bar based on price level.  Ratings appear to be pretty good... there is no accounting for
        taste, or lack there of.

        :return:
        """

        n_sites, median_rating = self._get_keyword('bar', minprice=1, maxprice=1)

        return n_sites, median_rating

    def get_yoga(self):
        """

        Find yoga studios

        :return:
        """

        n_sites, median_rating = self._get_keyword('yoga', no_price_restriction=True)

        return n_sites, median_rating

    def get_upscale_grocery(self):
        """

        TOOD: How do we retrieve TraderJoes and Whole Foods in one go?


        :return:
        """

        keyword_in = urllib.parse.quote('Whole Foods')

        n_sites, median_rating = self._get_keyword(keyword_in)

        return n_sites, median_rating

    def get_upscale_coffee(self):
        """

        :return:
        """

        n_sites, median_rating = self._get_keyword('coffee', minprice=2, maxprice=5)

        return n_sites, median_rating

    def get_gym(self):
        """
        Number and ratings of gym fitness facilities

        :return:
        """

        n_sites, median_rating = self._get_keyword('gym')

        return n_sites, median_rating

    def get_gas_station(self):
        """
        Number and ratings of gas / service stations

        :return:
        """
        keyword_in = urllib.parse.quote('Whole Foods')

        n_sites, median_rating = self._get_keyword(keyword_in)

        return n_sites, median_rating

    def get_liquor_store(self):
        """
        Number of liquor stores

        :return:
        """

        n_sites, median_rating = self._get_keyword('liquor+store')

        return n_sites, median_rating

    def get_nail_salon(self):
        """
        Number of nail salons

        :return:
        """

        n_sites, median_rating = self._get_keyword('nail+salon')

        return n_sites, median_rating

    def get_check_cashing(self):
        """
        Number of check cashing or payday loan

        :return:
        """

        n_sites, median_rating = self._get_keyword('check+cashing')

        return n_sites, median_rating

    # TODO: Finish this class
    # def enrich_poi(self):
    #     """
    #     Collect asset environment data and write a record to the DB
    #
    #
    #     :return:
    #     """
    #
    #     # Geocoding Results
    #     n_rest, rate_rest = self.get_restaurants()
    #     n_good_bar, rate_good_bar = self.get_good_bars()
    #     n_good_coffee, rate_good_coffee = self.get_upscale_coffee()
    #     n_gym, rate_gym = self.get_gym()
    #     n_yoga, rate_yoga = self.get_yoga()
    #     n_good_grocery, rate_good_grocery = self.get_upscale_grocery()
    #     n_gas, rate_gas = self.get_gas_station()
    #     n_bad_bar, rate_bad_bar = self.get_bad_bars()
    #     n_liquor_store, rate_liquor_store = self.get_liquor_store()
    #     n_nails, rate_nails = self.get_nail_salon()
    #     n_check_cashing, rate_check_cashing = self.get_check_cashing()
    #     # Distance Measures
    #     d_wholefoods=0
    #     d_traderjoes=0
    #
    #     # Census results
    #     dist_tech_bus_stop = 0
    #
    #     # TODO: Fill in these items
    #     med_hh_income = 0
    #     edu_attain = 0
    #     employment = 0
    #     own_house = 0
    #     proportion_income_rent = 0
    #
    #     # Write observations to DB
    #     envi = AssetEnvironment(asset_id=self.asset_id, # If recording data for an existing asset, else Null
    #                             # This field allows us to collect multiple samples for a given place, and observe trends over time
    #                             date_observed=datetime.date.today(),
    #                             observation_radius_m=self.radius,
    #
    #                             # up_scale_grocery: Whole Foods, trader joes, local organic $$$ grocery.
    #                             dist_wholefoods=d_wholefoods,
    #                             dist_traderjoes=d_traderjoes,
    #                             n_good_grocery=n_good_grocery,
    #
    #                             # Restraunts and bars with high stars and $$$+.  N
    #                             n_good_dinning=n_rest,
    #                             n_good_bars=n_good_bar,
    #                             n_good_coffee=n_good_coffee,
    #                             n_bad_bars=n_bad_bars,
    #                             n_gym=n_gym,
    #                             n_yoga=n_yoga,
    #                             n_gas_station=n_gas,
    #
    #                             # Liquor stores and dive bars
    #                             n_liquor_store=n_liquor_store,
    #                             n_nail_salon=n_nails,
    #                             # n_hair_salon=
    #                             n_check_cashing =n_check_cashing,
    #
    #                             # Jobs
    #                             # dist_tech_bus_stop =
    #
    #                             med_hh_income=0,
    #                             edu_attain=0,
    #                             employment=0,
    #                             own_house=0,
    #                             proportion_income_rent=0,
    #                             school_score=0,
    #                             walk_score0=0)
    #
    #     session.add(envi)




