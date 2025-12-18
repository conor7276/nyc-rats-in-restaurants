import requests
import urllib3
from pathlib import Path
import logging
import os
from sodapy import Socrata
from dotenv import load_dotenv, dotenv_values

env_path = Path(__file__).resolve().parent.parent / "secrets.env"
env_vars = dotenv_values(env_path)
print(env_path)
print(env_vars)

domain = 'https://data.cityofnewyork.us'
dataset_id = 'p937-wjvj'
endpoint = 'https://data.cityofnewyork.us/api/v3/views/p937-wjvj/query.json'
# USE POST when requesting
print(requests.post(endpoint))
client = Socrata(
    domain,
    app_token = env_vars['API_KEY'],
    timeout = 10
)

print(client)

data = client.get(dataset_id, limit = 2)

print(data)