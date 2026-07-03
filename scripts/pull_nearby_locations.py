import pandas as pd
import numpy as np
import requests
import time
import json
from dotenv import load_dotenv, dotenv_values
from pathlib import Path
import os
from fuzzywuzzy import fuzz
import argparse
import logging
from datetime import datetime

# Read in environment variables
parser = argparse.ArgumentParser()
parser.add_argument("--start-date", required=True)
parser.add_argument("--end-date", required=True)
parser.add_argument("--manual-start-date", default = "")
parser.add_argument("--manual-end-date", default = "")
parser.add_argument("--dry-run", default="false")
args = parser.parse_args()

geoapify_key = os.getenv('GEOAPIFY_KEY')

# Set up logger
logging.basicConfig(level = logging.INFO, format = '%(message)s')
logger = logging.getLogger(__name__)

# Resolve environment variables
# Differentiate between manual and automated run
logger.info(f"Dates: {args.manual_start_date} {args.manual_end_date}")
if args.manual_start_date and args.manual_end_date:
    start_date = datetime.strptime(args.manual_start_date, "%Y-%m-%d").date().isoformat()
    end_date = datetime.strptime(args.manual_end_date, "%Y-%m-%d").date().isoformat() 
    logger.info(f"Using manual run dates {start_date} and {end_date}")
else:
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date().isoformat()
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date().isoformat()
    logger.info(f"Using auto run dates {start_date} and {end_date}")


# establish directories
input_dir = Path("data/raw_data")
input_dir.mkdir(parents=True, exist_ok=True)
output_dir = Path("data/intermediate_data")
output_dir.mkdir(parents=True, exist_ok=True)
input_filepath = input_dir / f"data_{start_date}_{end_date}.csv"
output_filepath = output_dir / f"data_{start_date}_{end_date}.csv"

logger.info("Data and environmnet variable paths loaded")

# Read data and environment variables
df = pd.read_csv(input_filepath, parse_dates= ['inspection_date', 'approved_date'])

logger.info("Reading in file.")

# Filter out bad coordinates
df = df.dropna(subset = ['longitude', 'latitude'])
df = df[(df['longitude'] != 0) & (df['latitude'] != 0)]

# Clean and combine address data for later processing
df['street_name'] = df['street_name'].apply(lambda x : x.title())
df['address'] = df.apply(lambda x : str(x['house_number']) + ' ' + x['street_name'] ,axis = 1)

# Turn dates from timestamp level to date level
df['inspection_date'] = df['inspection_date'].apply(lambda x : pd.Timestamp(year = x.year, month = x.month, day = x.day))
df['approved_date'] = df['approved_date'].apply(lambda x : pd.Timestamp(year = x.year, month = x.month, day = x.day))

# Select needed columns
df = df[
    ['inspection_type',
     'job_id',
     'job_progress',
     'house_number',
     'street_name',
     'address',
     'zip_code',
     'latitude',
     'longitude',
     'result',
     'inspection_date',
     'approved_date',
     'nta'
     ]
]

# Differentiate rodent data columns from API columns
df.columns = df.columns.str.lower() + '_interdata'

################################## Perform API actions #######################################

logger.info("Beginning API calls to get nearby locations.")

# Set API params
categories = "catering.restaurant,commercial.food_and_drink,catering.fast_food,catering.food_court,catering.bar"
radius = "50" # meters
max_locations_returned = "5"

# Create new dataframe to store new data
all_restaurants_df = pd.DataFrame()

# Get each coordinates from each row
for _ , row in df.iterrows():

    time.sleep(0.5)

    # Get coordinates for parameters
    longitude = str(row['longitude_interdata'])
    latitude = str(row['latitude_interdata'])

    # Build url
    url = f"https://api.geoapify.com/v2/places?categories={categories}&filter=circle:{longitude},{latitude},{radius}&bias=proximity:{longitude},{latitude}&limit={max_locations_returned}&apiKey={geoapify_key}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    res = json.loads(response.text)

    try:
        local_restaurant_df = pd.DataFrame([
            {
                **feature["properties"],
                "geo_lon": feature["geometry"]["coordinates"][0],
                "geo_lat": feature["geometry"]["coordinates"][1],
            }
            for feature in res["features"]
        ])

        local_restaurant_df['inspection_type_interdata'] = row['inspection_type_interdata']
        local_restaurant_df['job_id_interdata'] = row['job_id_interdata']
        local_restaurant_df['job_progress_interdata'] = row['job_progress_interdata']
        local_restaurant_df['house_number_interdata'] = row['house_number_interdata']
        local_restaurant_df['street_name_interdata'] = row['street_name_interdata']
        local_restaurant_df['address_interdata'] = row['address_interdata']
        local_restaurant_df['zip_code_interdata'] = row['zip_code_interdata']
        local_restaurant_df['latitude_interdata'] = row['latitude_interdata']
        local_restaurant_df['longitude_interdata'] = row['longitude_interdata']
        local_restaurant_df['result_interdata'] = row['result_interdata']
        local_restaurant_df['inspection_date_interdata'] = row['inspection_date_interdata']
        local_restaurant_df['approved_date_interdata'] = row['approved_date_interdata']
        local_restaurant_df['nta_interdata'] = row['nta_interdata']
        
        all_restaurants_df = pd.concat([all_restaurants_df, local_restaurant_df])
    except Exception as e:
        # Move on if no data is found
        continue

logger.info("API calls completed, beginning data processing.")

if all_restaurants_df.empty:
    # If no data was pulled
    logger.info("No locations were able to be found.")
    exit(0)

# Process data
selected_columns = [
    'name', 'county', 'city', 'postcode', 'district', 'suburb', 'housenumber', 'street', 'address_line2',
    'lon','lat', 'formatted', 'catering', 'commercial','house_number_interdata', 'street_name_interdata', 'address_interdata',
    'inspection_type_interdata', 'result_interdata', 'inspection_date_interdata', 'approved_date_interdata', 'nta_interdata'
    ]

# format address
geo_rest_df = all_restaurants_df.copy()
geo_rest_df['address_line2'] = geo_rest_df['address_line2'].apply(lambda x : x.split(',')[0].strip() if x else None)

# Some runs containted no commercial data.
try:
    geo_rest_df = all_restaurants_df[selected_columns]
except Exception as e:
    logger.warning("No commercial data available.")
    geo_rest_df = all_restaurants_df[selected_columns.remove('commercial')]
    geo_rest_df['commercial'] = pd.NA

requested_places_saved = geo_rest_df.copy()

# Logic is fuzzy with addresses we try to pick ones that are close to matching then compare numerical addresses
requested_places_saved['ratio'] = requested_places_saved.apply(lambda x: fuzz.WRatio(x['address_line2'], x['address_interdata']), axis=1)
requested_places_saved = requested_places_saved[requested_places_saved['ratio'] >= 80]

requested_places_saved['split_check'] = requested_places_saved.apply(lambda x : x['housenumber'] == x['house_number_interdata'], axis = 1)
requested_places_saved = requested_places_saved[requested_places_saved['split_check'] == True]

# Column cleanup
requested_places_saved[['lon', 'lat']] = requested_places_saved[['lon', 'lat']].round(6)
selected_columns = [
    'name', 'county', 'city', 'postcode', 'suburb', 'address_line2', 'address_interdata', 'lon', 'lat',
    'catering', 'commercial', 'inspection_type_interdata', 'inspection_date_interdata', 'approved_date_interdata', 'result_interdata', 'nta_interdata'
]
requested_places_saved = requested_places_saved[selected_columns]
requested_places_saved = requested_places_saved.rename(
    columns = {
        'address_line2' : 'address',
        'inspection_type_interdata' : 'inspection_type',
        'inspection_date_interdata' : 'inspection_date',
        'approved_date_interdata' : 'approved_date',
        'result_interdata' : "result",
        'nta_interdata' : 'neighborhood'}
)

def category_handler(catering, commercial):
    if pd.notnull(catering): # If it is a restaurant it will show the type of catering
        try:
            return catering['cuisine'].title().strip()
        except Exception as e:
            return 'N/A'
    else: # If it is not a restaurant it will show what other type of place it is eg: bar/supermarket
        try:
            return commercial['type'].title().strip()
        except Exception as e:
            return 'N/A'
        
requested_places_saved['type'] = requested_places_saved.apply(lambda x : category_handler(x['catering'], x['commercial']), axis = 1)
requested_places_saved = requested_places_saved.drop(columns = ['catering', 'commercial'])

# Handle addresses
requested_places_saved['address'] = requested_places_saved['address'].apply(lambda x : x.split(',')[0])
requested_places_saved = requested_places_saved.drop(columns = ['address_interdata'])

logger.info("Saving data to repo.")

requested_places_saved.to_csv(output_filepath, index = False)

logger.info(f"Data was successfully saved to repo. Preview of dataframe: {requested_places_saved.head()}")

