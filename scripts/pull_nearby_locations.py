import pandas as pd
from pathlib import Path
from dotenv import dotenv_values
from fuzzywuzzy import fuzz
import requests
import time
import logging

# Set up logger
logging.basicConfig(level = logging.INFO, format = '%(message)s')
logger = logging.getLogger(__name__)

# Resolve data and environment paths
data_path = Path(__file__).resolve().parent.parent / "data/raw_data/data_2025-12-15_2025-12-21.csv"
env_path = Path(__file__).resolve().parent.parent / "secrets.env"

logger.info("Data and environmnet variable paths loaded")

# Read data and environment variables
df = pd.read_csv(data_path)
env_vars = dotenv_values(env_path)
logger.info("Data and environment variables loaded.")

# Filter out bad coordinates
df = df.dropna(subset = ['longitude', 'latitude'])
df = df[(df['longitude'] != 0) & (df['latitude'] != 0)]

# Clean and combine address data for later processing
df['street_name'] = df['street_name'].apply(lambda x : x.title())
df['address'] = df.apply(lambda x : str(x['house_number']) + ' ' + x['street_name'] ,axis = 1)

logger.info("Raw data cleaned")

# Replace with your actual API Key
API_KEY = env_vars['GOOGLE_PLACES_API_KEY']

# The endpoint for the Nearby Search (New) API
url = "https://places.googleapis.com/v1/places:searchNearby"

# Define the request body as a Python dictionary
# This example searches for restaurants within a 500-meter radius
# around a specific latitude and longitude.
request_body = {
    "includedTypes": ["restaurant", "meal_delivery", "meal_takeaway", "bakery", "bar", "cafe"],
    "maxResultCount": 20,
    "locationRestriction": {
        "circle": {
            "center": {
                "latitude": 0,
                "longitude": 0
            },
            "radius": 25.0 # Turn back to 25
        }
    }
}
# Headers determine what contents of the restaurants are returned
headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.rating"
}

logger.info("Beginning to make requests for each location.")
requested_places = pd.DataFrame()

# Loop through rows
for row in df.head(100).iterrows():

    temp_df = pd.DataFrame()

    latitude = row[1]['latitude']
    longitude = row[1]['longitude']
    address = row[1]['address']
    
    try:
        # Makes POST request to google searchNearby API and returns json of nearby locations

        # Reset for every iteration
        request_body['locationRestriction']['circle']['center']['latitude'] = latitude
        request_body['locationRestriction']['circle']['center']['longitude'] = longitude

        # Make request
        response = requests.post(url, headers=headers, json=request_body)
        time.sleep(0.1)

        # Success == 200
        if response.status_code == 200:
            response_data = response.json()
            # print("Nearby Search Results:")
            if response_data and "places" in response_data:
                for place in response_data["places"]:
                    display_name = place.get("displayName", {}).get("text", "N/A")
                    formatted_address = place.get("formattedAddress", "N/A")
                    location = place.get("location", {})
                    rating = place.get("rating", "N/A")
            else:
                print("No places found or unexpected response format.")
        else:
            logger.error(f"Request failed with {response.status_code} at {row[0]} in data check Logger and {response.text} then rerun.")
            # print(f"Error: Request failed with status code {response.status_code}")
            # print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed with {response.status_code} at {row[0]} in data check Logger and {response.text} then rerun.")
        print(f"An error occurred: {e}")
    
    # Append to main dataframe if data is returned
    if response_data:
        temp_df = pd.DataFrame(response_data['places'])
        temp_df['latitude'] = latitude
        temp_df['longitude'] = longitude
        temp_df['address'] = address
        
        requested_places = pd.concat([requested_places, temp_df])
    else:
        print("Nothing returned!")
logger.info("Requestes finished and data combined.")

# Check for if any data is returned at all
if requested_places.empty == False:
    requested_places_saved = requested_places.copy()

    # Compare ratios between addresses to get correct original location
    requested_places_saved['ratio'] = requested_places_saved.apply(lambda x : fuzz.WRatio(x['formattedAddress'], x['address']), axis = 1)
    requested_places_saved = requested_places_saved[requested_places_saved['ratio'] >= 80]

    # Check number in address for final comparison
    requested_places_saved['split_check'] = requested_places_saved.apply(lambda x : x['formattedAddress'].split()[0] == x['address'].split()[0], axis = 1)
    requested_places_saved = requested_places_saved[requested_places_saved['split_check'] == True]

    requested_places_saved.to_csv(f"data/intermediate_data/data_{env_vars['MONDAY_LAST_WEEK']}_{env_vars['SUNDAY_LAST_WEEK']}.csv", index = False)
    logger.info("Address comparison and cleanup completed. File Saved to intermediate data folder.")
else:
    # if no data is returned at all
    logger.info("No Data was able to be found.")
    print("No locations were found that failed inspection. Check Logs!")