#
#   rentals.py
#   ~~~~~~~~~~
#
#   Web-scraper data collectors for rental listing websites
#
import re
import datetime
import time
import random

import requests
import numpy as np
from bs4 import BeautifulSoup as bsoup
from sqlalchemy import and_

from assets.asset import RentalListing


def beds(attrib_list):
    """
        Apply regex patterns to extract beds from list of attribute strings

        Attempts to cast return value as float
    """

    br = '\d*BR'        # Match CL style number of beds pattern

    return two_step_searcher(attrib_list, br)


def baths(attrib_list):
    """
        Apply regex patterns to extract beds from list of attribute strings

        Attempts to cast return value as float
    """

    ba = '\d*Ba'

    return two_step_searcher(attrib_list, ba)


def rental_area(attrib_list):
    """
        Apply regex patterns to extract square footage of rental if available

        Attempts to cast return value as float
    :param attrib_list:
    :return:
    """

    ba = re.compile('\d*ft2')

    return two_step_searcher(attrib_list, ba)


def two_step_searcher(attrib_list, s_one, s_two='\d*'):
    """
        General two step matcher finds a string matching p1 in a list of strings, then extracts float value with p2

        If pattern p2 cannot be cast as float, -1.0 will be returned

    :param attrib_list:
    :param s_one: First string to look for in attribute
    :param s_two: Second pattern, default is any number
    :return:
    """
    
    # Compile regex patterns
    p_one = re.compile(s_one)
    p_two = re.compile(s_two)

    for attrib in attrib_list:

        is_match = p_one.search(attrib)

        if is_match:

            str_match = is_match.group()

            try:

                out = float(p_two.search(str_match).group())

                return out

            except ValueError:

                return -1.0

        else:

            return -1.0


def find_prices(results):
    prices = []
    for rw in results:
        price = rw.find('span', {'class': 'price'})
        if price is not None:
            price = float(price.text.strip('$'))
        else:
            price = np.nan
        prices.append(price)
    return prices


class CraigsList:
    """
    Class to orchestrate CL scraping of housing rental data

    Example URL for houses in Richmond
    https://sfbay.craigslist.org/search/eby/apa?nh=65&availabilityMode=0&housing_type=6&sale_date=all+dates

    Housing types:
    Apartment => housing_type=1
    House => housing_type=6
    In law => housing_type=7
    townhouse => housing_type=9
    Duplex => housing_type=4

    """

    def __init__(self, neighborhood, housing_type_name, config):

        self.neighborhood = neighborhood
        self.housing_type_name = housing_type_name
        self.base_url = config["base_url"]
        self.config = config
        self.txt = None
        self.nh = 0
        self.housing_type = 0

        self.set_housing_type_id()
        self.set_neighborhood_id()

    def set_neighborhood_id(self):
        """ Map neighborhood string to API ID int """
        self.nh = self.config['neighborhoods'][self.neighborhood]

    def set_housing_type_id(self):
        """ Map housing type sting to API ID int """
        self.housing_type = self.config['housing_types'][self.housing_type_name]

    def add_if_new(self, listing, session):
        """ If listing is not present in DB, add (insert it) it """

        if session.query(RentalListing).filter(and_(RentalListing.source_id == listing.source_id,
                                                    RentalListing.source == listing.source)).count() == 0:
            # No record for this listing exists in DB, so proceed with insert
            session.add(listing)
            print('-- Completed DB insert of listing {} --'.format(listing.source_id))
        else:
            print('-- Dup, not inserting {}'.format(listing.source_id))

        return

    def get_listings(self, session):
        """ Scrape CL and store rental data in database via session """

        # Assemble payload
        payload = {'nh': self.nh, 'availabilityMode': 0, 'housing_type': self.housing_type, 'sale_date': 'all+dates'}

        # Make the web service call
        resp = requests.get(self.base_url, params=payload)

        # TODO: Make sure response is 200

        # Parse results to text
        self.txt = bsoup(resp.text, 'html.parser')

        # Find number of listing results returned
        num_listings = int(self.txt.find('span', class_="totalcount").text)

        if num_listings < 120:
            # If this number is < 120, one page, else need to work through pages with query param
            #
            #   Initial page https://sfbay.craigslist.org/search/apa?availabilityMode=0&housing_type=6&sale_date=all+dates
            #   Second page https://sfbay.craigslist.org/search/apa?s=120&availabilityMode=0&housing_type=6
            #   Third page  https://sfbay.craigslist.org/search/apa?s=240&availabilityMode=0&housing_type=6
            #                                                        "s" above incrementing by 120

            # Create a list of results objects
            listings = self.txt.find_all('li', class_='result-row')

            # For each object extract elements of interest
            for ind in range(len(listings)):

                li_data_id = int(listings[ind].find(class_="result-title hdrlnk").get("data-id"))
                li_title = listings[ind].find(class_="result-title hdrlnk").text

                li_date_str = listings[ind].find(class_="result-date").get("datetime")
                li_date = datetime.datetime.strptime(li_date_str,'%Y-%m-%d %H:%M')

                # Strip "$" off rent figure  TODO: Need to handle exception if fails?
                li_rent = float(listings[ind].find(class_='result-price').text.replace('$', ''))

                li_href = listings[ind].find(class_="result-title hdrlnk").get('href')

                # Create RentalListing Object (SQL Alchemy Class)
                listing = RentalListing(source_id=li_data_id,
                                        title=li_title,
                                        rent=li_rent,
                                        url=li_href,
                                        date_listed=li_date,
                                        source='cl',
                                        property_type=self.housing_type_name,
                                        neighborhood=self.neighborhood,
                                        )

                # Retrieve listing details link, for more details on the property
                # TODO Add random wait here

                # Wait up to 30 sec between scrapes
                wait_time = random.randint(1, 30)

                time.sleep(wait_time)
                resp_li = requests.get(li_href)
                txt_li = bsoup(resp_li.text, 'html.parser')

                try:
                    listing.latitude = txt_li.find('div', class_='viewposting').get("data-latitude")
                    listing.longitude = txt_li.find('div', class_='viewposting').get("data-longitude")
                except AttributeError:
                    # Not all listings have lat-long
                    listing.latitude = ''
                    listing.longitude = ''

                listing.description = txt_li.find('section', id="postingbody").text  # Text description of listing

                # Find structured property attributes, then clean-up and tokenize them
                txt_attrib = txt_li.find_all('p', class_="attrgroup")

                txt_li_attribs = []
                for attribs in txt_attrib:
                    raw_attribs = attribs.text.split('\n')
                    keepers = [x for x in raw_attribs if x != '']
                    txt_li_attribs += keepers

                listing.attributes = txt_li_attribs

                # TODO: Add parking
                # TODO: Add laundry

                # Extract beds, baths, etc. from attributes
                listing.beds = beds(txt_li_attribs)
                listing.baths = baths(txt_li_attribs)
                listing.building_area = rental_area(txt_li_attribs)

                # TODO: Collect images

                # Now listing object is complete, save to database
                self.add_if_new(listing, session)
                # session.add(listing)

                session.commit()

        else:
            # If number is greater than 120, iterate through pages of results
            # TODO: Complete this
            raise NotImplementedError