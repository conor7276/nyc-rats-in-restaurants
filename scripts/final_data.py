from pathlib import Path
import pandas as pd
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# args may be used later
parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", default="false")
args = parser.parse_args()

logger.info("Preparing Final Data.")
input_path = Path('data/intermediate_data')

logger.info("Paths Loaded.")

df= pd.DataFrame()

logger.info("Loading Intermediate Data Files.")
for file in input_path.glob("*.csv"):
    df = pd.concat([df, pd.read_csv(file, parse_dates = ['inspection_date'])])

logger.info("Data Combined")

df = df.sort_values(by = "inspection_date", ascending = False)

df = df.head(500)

output_dir = Path("data/final_data")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / f"final_rat_data.csv"
df.to_csv(output_path, index = False)

logger.info(f"Saving data to {output_path} successfully.")