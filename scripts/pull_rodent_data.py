import logging
from sodapy import Socrata
from datetime import datetime
import os
import argparse
from pandas import DataFrame
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# ------------------ ARGUMENTS ------------------
parser = argparse.ArgumentParser()
parser.add_argument("--start-date", required=True)
parser.add_argument("--end-date", required=True)
parser.add_argument("--manual-start-date", default = "")
parser.add_argument("--manual-end-date", default = "")
parser.add_argument("--dry-run", default="false")
args = parser.parse_args()

# Differentiate between manual and automated run
if args.manual_start_date and args.manual_end_date:
    start_date = datetime.strptime(args.manual_start_date, "%Y-%m-%d").date().isoformat()
    end_date = datetime.strptime(args.manual_end_date, "%Y-%m-%d").date().isoformat() 
    logger.info(f"Using manual run dates {start_date} and {end_date}")
else:
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date().isoformat()
    start_date = datetime.strptime(args.end_date, "%Y-%m-%d").date().isoformat()
    logger.info(f"Using auto run dates {start_date} and {end_date}")

# ------------------ ENV VARS ------------------
logger.info("Getting environment variables.")
app_token_api_key = os.getenv('APP_TOKEN_API_KEY')

if not app_token_api_key:
    raise ValueError("APP_TOKEN_API_KEY is missing.")

# ------------------ SOCRATA CONNECTION ------------------
DOMAIN = 'data.cityofnewyork.us'
DATASET_ID = 'p937-wjvj'

logger.info("Connecting to NYC Open Data")
client = Socrata(DOMAIN, app_token=app_token_api_key, timeout=10)

# ------------------ DATA PULL ------------------
try:
    logger.info(f"Pulling data from {start_date} to {end_date}")
    data = client.get(
        DATASET_ID,
        where=f"""
            inspection_date >= '{start_date}' AND
            inspection_date <= '{end_date}' AND
            result != 'Passed'
        """,
        limit=1000
    )
except Exception as e:
    logger.error(f"Data pull failed: {e}")
    data = []

# ------------------ SAVE DATA ------------------
logger.info("Creating dataframe.")
df = DataFrame(data)

if not df.empty:
    output_dir = Path("data/raw_data")
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / f"data_{start_date}_{start_date}.csv"
    df.to_csv(filepath, index=False)
    logger.info(f"Saved data to {filepath}")
    logger.info(f"Data Preview: ")
    logger.info(df.head())
else:
    logger.info("No data returned.")
