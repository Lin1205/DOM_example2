#
#   SQLite DB initialization script
#
#   This script will initialize tables required by data capture app
#
import sqlite3

conn = sqlite3.connect('assets.db')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE assets 
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
c.execute('''CREATE TABLE transactions
             (asset_id INT,
              listing_type INT,
              list_price REAL,
              sale_price REAL,
              days_on_market REAL,
              listing_agent_id INT,
              status INT)''')

# Rental Data
c.execute('''CREATE TABLE rentals
             (asset_id INT,
              rental_listing_type INT,
              monthly_price REAL,
              utilities_included INT,
              extra_fees INT,
              days_on_market REAL,
              status INT)''')

# JSON details
c.execute('''CREATE TABLE asset_data
             (id INT, 
              details)''')

# create table department (name, employees);
# insert into department (name, employees) values("library", json('{"surname":"Smith", "name":"John"}'));
# select json_extract(department.employees, '$.surname') from department;
