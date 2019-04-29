#
#   Class to represent an asset w/o
#
#
#   An alternative Asset implementation, for looser coupling to SQLAlchemy
#
#
#
import pandas as pd


class Asset:
    """
    A class that represents one asset

    """

    def __init__(self):
        """ Initialize object fields matching asset DB """
        self.asset_id = 0
        self.description = ''
        self.asset_id = 0
        self.status = ''
        self.asset_type = 0
        self.price = 0.0
        self.property_type = ''
        self.address = ''
        self.city = ''
        self.state = ''
        self.country = ''
        self.zip = 0
        self.zip_four = 0
        self.location = ''
        self.beds = 0
        self.baths = 0
        self.building_area = 0.0
        self.lot_area = 0.0
        self.year_built = 0
        self.hoa_per_month = 0.0
        self.url = ''
        self.source = ''
        self.mls_number = ''
        self.latitude = 0.0
        self.longitude = 0.0
        self.days_on_market = 0
        self.walk_score = 0.0
        self.transit_score = 0.0
        self.floors = 0
        self.parking_spaces = 0
        self.garage_spaces = 0

    def to_db(self):
        """ Save current asset to asset DB """
        pass


class RentalListing(Asset):
    """ Object used to describe an asset listed for rent """
    pass


class Assets:
    """
    A class that contains a set of assets

    """
    def __init__(self):
        self.assets = pd.DataFrame()

    def read_redfin(self, file_path):
        """ Import redfin data """

        raw_assets = pd.read_csv(file_path, parse_dates=[1])

        raw_assets = raw_assets.drop_duplicates()

        self.assets = raw_assets

    def read_mls(self, file_path):
        """ Import MLS data """
        pass

    # def to_db(self):
    #     """ Save asset records to asset DB """
    #
    #     self.assets.to_sql(name=ASSETS_TABLE, con=db_con, if_exists='append',
    #                        # index_label='asset_id',
    #
    #
    #
    #                        )