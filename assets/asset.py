#
#   asset.py
#   ~~~~~~~~
#
#   SQLAlchemy Classes Representing Assets
#
#
from sqlalchemy import Column, Integer, String, Date, Float, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, create_engine

DB_PATH = 'sqlite:////Users/andy/PycharmProjects/real_estate/asset.db'


# Instantiate SQLAlchemy declarative base object
Base = declarative_base()


class Asset(Base):
    """
    A class that represents an asset, and uses the SQLAlchemy ORM

    """
    __tablename__ = 'asset'

    # Define columns for assets table, and instance attributes for class
    asset_id = Column(Integer, primary_key=True)
    description = Column(String(250), nullable=False)
    status = Column(String(250), nullable=False)
    asset_type = Column(Integer)
    price = Column(Float, nullable=True)
    property_type = Column(String(250), nullable=False)
    address = Column(String(250), nullable=False)
    city = Column(String(250), nullable=False)
    state = Column(String(250), nullable=False)
    country = Column(String(250), nullable=False)
    zip = Column(Integer, nullable=False)
    zip_four = Column(Integer, nullable=True)
    location = Column(String(250), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    block_fips = Column(String(250), nullable=True)
    county_fips = Column(String(250), nullable=True)
    county_name = Column(String(250), nullable=True)
    state_fips = Column(String(250), nullable=True)
    state_name = Column(String(250), nullable=True)
    beds = Column(Float, nullable=False)
    baths = Column(Float, nullable=False)
    building_area = Column(Float, nullable=False)
    lot_area = Column(Float, nullable=False)
    year_built = Column(Date, nullable=False)
    hoa_per_month = Column(Float, nullable=False)       # Zero if N/A
    url = Column(String(250), nullable=True)
    source = Column(String(250), nullable=False)
    mls_number = Column(String(250), nullable=True)
    date_listed = Column(Date, nullable=False)          # Use this for computing days on market
    date_sold = Column(Date, nullable=False)            # Use this for computing days on market
    walk_score = Column(Float, nullable=False)
    transit_score = Column(Float, nullable=False)
    floors = Column(Integer, nullable=False)
    parking_spaces = Column(Integer, nullable=False)
    garage_spaces = Column(Integer, nullable=False)


class RentalListing(Base):
    """
    A class that describes an asset listed for rent, and uses the SQLAlchemy ORM

    This table is minimal because it supports the scraper server.  After upload to the back end, enrichers can
    add additional data elements.

    rent: Monthly rent in dollars

    """
    __tablename__ = 'rental_listing'

    listing_id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer)
    asset_id = Column(Integer, ForeignKey("asset.asset_id"), nullable=True)
    date_listed = Column(Date, nullable=False)
    title = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    source = Column(String(250), nullable=False)        # Could convert to INT metadata later
    property_type = Column(String(250), nullable=False)
    latitude = Column(String(50), nullable=False)
    longitude = Column(String(50), nullable=False)
    neighborhood = Column(String(250))
    address = Column(String(250), nullable=True)
    city = Column(String(250), nullable=True)       # In practice, we will not let this be null, but it may be initially
    state = Column(String(250), nullable=True)
    # county = Column(String(250), nullable=True)
    # country = Column(String(250), nullable=True)
    # zip = Column(Integer, nullable=True)
    # block_fips = Column(String(250), nullable=False)
    # county_fips = Column(String(250), nullable=False)
    # county_name = Column(String(250), nullable=False)
    # state_fips = Column(String(250), nullable=False)
    # state_name = Column(String(250), nullable=False)
    rent = Column(Float, nullable=False)
    beds = Column(Float, nullable=False)
    baths = Column(Float, nullable=True)
    parking_spaces = Column(Integer, nullable=True)
    # images = Column(String(250), nullable=True)  # path to images from listing
    # garage_spaces = Column(Integer, nullable=False)
    url = Column(String(250), nullable=True)  # URL of source listing
    # lease_term_months = Column(Integer, nullable=False)
    attributes = String      # TODO: Make something like Column(ARRAY(String))
    building_area = Column(Float, nullable=True)

    def __repr__(self):

        return "<RentalListing(listing_id={:.0f}, source_id={}, title={}, neighborhood={}, rent=${:.0f})>".format(
                self.listing_id, self.source_id, self.title, self.neighborhood, self.rent)

# class Neighborhood(Base):
#     """
#     A class that represents an area of interest or neighborhood
#
#     Class attributes describe attractiveness of neighborhood
#
#
#     """
#     __tablename__ = 'rental_listing'
#
#     dist_wholefoods =
#     dist_traderjoes =
#     dist_tech_bus_stop =
#     dist_gas_station =
#     good_dinning =
#     good_drinking =
#     bad_drinking =

class AssetEnvironment(Base):
    """
    A class that captures information about the environment around an asset

    """

    __tablename__ = 'environment'

    asset_env_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("asset.asset_id"), nullable=True)

    # This field allows us to collect multiple samples for a given place, and observe trends over time
    date_observed = Column(Date, nullable=False)
    observation_radius_m = Column(Float, nullable=False) # Search radius for observations below

    # up_scale_grocery: Whole Foods, trader joes, local organic $$$ grocery.
    dist_wholefoods = Column(Float, nullable=False)
    dist_traderjoes = Column(Float, nullable=False)
    n_good_grocery = Column(Integer, nullable=False)

    # Restraunts and bars with high stars and $$$+.  N
    n_good_dinning = Column(Integer, nullable=False)
    n_good_bars = Column(Integer, nullable=False)
    n_good_coffee = Column(Integer, nullable=False)
    n_gym = Column(Integer, nullable=False)
    n_yoga = Column(Integer, nullable=False)
    # n_childcare = Column(Integer, nullable=False)
    n_gas_station = Column(Integer, nullable=False)


    # Liquor stores and dive bars
    n_bad_bars = Column(Integer, nullable=False)
    n_liquor_store = Column(Integer, nullable=False)
    n_nail_salon = Column(Integer, nullable=False)
    # n_hair_salon = Column(Integer, nullable=False)
    n_check_cashing = Column(Integer, nullable=False)

    # Jobs
    # dist_tech_bus_stop = Column(Integer, nullable=True)

    med_hh_income = Column(Integer, nullable=False)
    edu_attain = Column(Integer, nullable=False)
    employment = Column(Integer, nullable=False)
    own_house = Column(Integer, nullable=False)
    proportion_income_rent = Column(Integer, nullable=False)

    school_score = Column(Float, nullable=True)
    walk_score = Column(Float, nullable=True)

if __name__ == "__main__":
    # Create an engine to store data at specified path
    engine = create_engine(DB_PATH)

    # Create tables in the engine.  This is SQLAlchemy's equivalent of CREATE TABLE...
    Base.metadata.create_all(engine)

