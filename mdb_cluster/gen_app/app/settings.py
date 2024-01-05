import os
from dotenv import load_dotenv
import logging

# logging.basicConfig(level=logging.INFO, format="[%(levelname)s]::%(message)s")
logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s][%(asctime)s]:%(message)s"
)
# start 2023-12-27 21:49:14,706

# waiting secs for reloading data
gen_data_waiting_for_reload = 0.1 * 60

# waiting secs for next api call
gen_data_waiting_for_apicall = 0

# waiting secs for next api call on error
gen_data_waiting_for_apicall_on_error = 3

# start pulling data from year
gen_data_movie_since_year = 1900

# limit of number of page in API call
PAGE_COUNT_LIMIT = 500


# genre list for pulling movie info
genre_list = [
    [35, "Comedy"],
    [99, "Documentary"],
    [27, "Horror"],
    [28, "Action"],
]

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
