import requests
import urllib3
from pathlib import Path
import logging
import os
from sodapy import Socrata
from dotenv import dotenv_values, set_key
from datetime import date


logging.basicConfig(level = logging.INFO, format = '%(message)s')
logger = logging.getLogger(__name__)

# Get environment variables
logger.info("Getting environment variables to pull from NYC Open Data.")
env_path = Path(__file__).resolve().parent.parent / "secrets.env"
env_vars = dotenv_values(env_path)


# do not use an https
DOMAIN = 'data.cityofnewyork.us'
DATASET_ID = 'p937-wjvj'

logger.info("Connecting to Database")
# APP_TOKEN_API_KEY
client = Socrata(
    DOMAIN,
    app_token = env_vars['APP_TOKEN_API_KEY'],
    timeout = 10
)

monday_last_week = date(2025,12,15).isoformat()
sunday_last_week = date(2025,12,21).isoformat()

try:
    logging.info("Pulling this weeks data.")
    data = client.get(
        DATASET_ID,
        select = """*""",
        where = f"""
            inspection_date >= '{monday_last_week}' AND
            inspection_date <= '{sunday_last_week}' AND
            result != 'Passed'
        """,
        limit =1000)
    
except Exception as e:
    logger.info(f"Data pull failed with error {e}")


from pandas import DataFrame

logging.info("Creating dataframe for pulled data.")
data = DataFrame(data)

if data.empty == False:
    data.to_csv(f"data/raw_data/data_{monday_last_week}_{sunday_last_week}.csv", index = False)

    logger.info(f"Data for the week of {monday_last_week} through {sunday_last_week} saved.")

    set_key(dotenv_path=env_path, key_to_set="MONDAY_LAST_WEEK", value_to_set=monday_last_week)
    set_key(dotenv_path=env_path, key_to_set="SUNDAY_LAST_WEEK", value_to_set=sunday_last_week)

    logger.info("Environment keys updated.")
else:
    logger.info(f"No data was avaliable for th week of {monday_last_week} through {sunday_last_week}")
