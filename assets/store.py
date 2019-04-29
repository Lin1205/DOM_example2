#
#   Module to manage persistent storage of asset data
#
#
#
import os
import sqlite3

SQLITE_DB_NAME = 'assets.db'

def create_sqlite(db_path): 
    """ Create assets db if it does not exist

    :return:
    """

    # Check if db exists at path provided
    db_full_path = os.path.join(db_path, SQLITE_DB_NAME)

    try:

        stat = os.stat(db_full_path)
        print('DB exists at {}, exiting without initializing a new DB.'.format(db_full_path))
        print(stat)

    except FileNotFoundError:

        # Create db
        conn = sqlite3.connect(os.path.join(db_path, SQLITE_DB_NAME))

        con = conn.cursor()

        # Create table
        con.execute('''CREATE TABLE assets 
                     (asset_id INT, 
                      status CHARACTER(20),
                      asset_type INT,  
                      price REAL,
                      property_type CHARACTER(20),
                      address VARCHAR(255), 
                      city VARCHAR(255), 
                      state CHARACTER(20),
                      country CHARACTER(20),
                      zip INT, 
                      zip_four INT,    
                      location VARCHAR(255),
                      beds INT,
                      baths INT,
                      building_area REAL, 
                      lot_area REAL,
                      year_built INT,
                      hoa_per_month REAL, 
                      url VARCHAR(255), 
                      source VARCHAR(255), 
                      mls_number VARCHAR(255), 
                      latitude REAL,
                      longitude REAL,
                      days_on_market INT,
                      walk_score REAL,
                      transit_score REAL,
                      floors INT,
                      parking_spaces INT,
                      garage_spaces INT
                      )''')

        # Transaction Data
        con.execute('''CREATE TABLE transactions
                     (asset_id INT,
                      listing_type INT,
                      list_price REAL,
                      sale_price REAL,
                      days_on_market REAL,
                      listing_agent_id INT,
                      status INT)''')

        # Rental Data
        con.execute('''CREATE TABLE rentals
                     (asset_id INT,
                      rental_listing_type INT,
                      monthly_price REAL,
                      utilities_included INT,
                      extra_fees INT,
                      days_on_market REAL,
                      status INT)''')

        # JSON details
        con.execute('''CREATE TABLE asset_data
                     (id INT, 
                      details)''')

        con.close()
