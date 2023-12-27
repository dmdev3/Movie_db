import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s]::%(message)s")

# waiting secs for reloading data
gen_data_waiting_for_reload = 0.9 * 60

# waiting secs for next api call
gen_data_waiting_for_apicall = 0

# start pulling data from year
gen_data_movie_since_year = 1950

load_dotenv()
try:
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")
    db_name = os.environ.get("DB_NAME")

    api_key = os.environ.get("API_KEY")
except Exception as e:
    logging.critical(f"Error in loading settings: {e}")
