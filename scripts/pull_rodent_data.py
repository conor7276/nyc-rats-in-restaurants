import requests
import urllib3
from pathlib import Path
import logging
import os
from sodapy import Socrata
from dotenv import load_dotenv, dotenv_values
from datetime import date

env_path = Path(__file__).resolve().parent.parent / "secrets.env"
env_vars = dotenv_values(env_path)
print(env_path)
print(env_vars)

# do not use an https
DOMAIN = 'data.cityofnewyork.us'
DATASET_ID = 'p937-wjvj'


# APP_TOKEN_API_KEY
client = Socrata(
    DOMAIN,
    app_token = env_vars['APP_TOKEN_API_KEY'],
    timeout = 10
)

print(client)

monday_last_week = date(2025,12,8).isoformat()
sunday_last_week = date(2025,12,14).isoformat()

data = client.get(
    DATASET_ID,
    select = """*""",
    where = f"""
        inspection_date >= '{monday_last_week}' AND
        inspection_date <= '{sunday_last_week}' AND
        result != 'Passed'
    """,
    limit =1000)

# print(data)

import pandas as pd

data = pd.DataFrame(data)
print(data.head())
data.to_csv("data.csv", index = False)