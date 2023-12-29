import logging
import time
import datetime
import requests
import json
import psycopg2
import uuid
import settings
import init_db as storage


def save_movie_object(movie_year, blocked_page, json_data):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM movie_data WHERE value1 = %s AND value2 = %s ;",
            (
                str(movie_year),
                str(blocked_page),
            ),
        )

        # get movie list
        for movie in json_data.get("results", []):
            cursor.execute(
                "INSERT INTO movie_data (value1, value2, json_data) VALUES (%s, %s, %s)",
                (
                    movie_year,
                    blocked_page,
                    json.dumps(movie),
                ),
            )
        conn.commit()
        cursor.close()
    except Exception as e:
        logging.critical(f" Error in operation with db {e}")
    pass


worker_name = str(uuid.uuid4())

base_url = "https://api.themoviedb.org/3"
# Endpoint for discovering movies
discover_endpoint = f"{base_url}/discover/movie"
PAGE_COUNT_LIMIT = 500
genre_list = settings.genre_list

# waiting secs for reloading data
waiting_for_reload = settings.gen_data_waiting_for_reload
waiting_for_apicall = settings.gen_data_waiting_for_apicall

movie_since_year = settings.gen_data_movie_since_year
movie_to_year = int(datetime.date.today().year)
# Parameters for the request
params = {
    "api_key": settings.api_key,
    "sort_by": "original_title.asc",
    "primary_release_year": movie_since_year,
    "page": 1,  # Page number (adjust as needed)
    "language": "en-US",  # Language for results
}

movie_counts = []

while True:
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
        )
        storage.create_db_objects(conn)

        # Pulling data by API to db
        while True:
            try:
                # Getting the last year, page
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT "
                    " CAST(value1 AS INT) as movieyear"
                    " ,CAST(value2 AS INT) as page"
                    " ,CASE WHEN CURRENT_TIMESTAMP - created_at > INTERVAL '2 minutes' AND json_data IS NULL THEN 1 ELSE 0 END AS LostRecords"
                    " ,(SELECT (json_data -> 'total_pages')::integer "
                    "   FROM movie_by_page as im "
                    "   WHERE im.value1 = om.value1 and (json_data -> 'total_pages') IS NOT NULL "
                    "   ORDER BY value2::int DESC "
                    "   LIMIT 1) "
                    " AS totalpages"
                    " FROM movie_by_page as om"
                    " ORDER BY LostRecords DESC, movieyear DESC, page DESC"
                    " LIMIT 1"
                )
                result = cursor.fetchall()

                # Define start_year
                if len(result) == 0:
                    blocked_year = movie_since_year
                    blocked_page = 0
                    blocked_flag = 0
                    total_pages = -1
                else:
                    blocked_year = result[0][0]
                    blocked_page = result[0][1]
                    blocked_flag = result[0][2]
                    # if we do not have total pages in json, we need to continue increment page, if pages>pages_limit, set limit
                    total_pages = result[0][3] if result[0][3] else -2
                    if result[0][3] is None:
                        total_pages = -2
                    elif result[0][3] > PAGE_COUNT_LIMIT:
                        total_pages = PAGE_COUNT_LIMIT
                    else:
                        total_pages = result[0][3]

                if blocked_flag == 0:
                    if blocked_year == movie_to_year and blocked_page == total_pages:
                        # data was loaded we can finish the process
                        break
                    else:
                        # continue loading process from existing year, page + 1
                        if blocked_page >= total_pages and total_pages > -1:
                            blocked_page = 1
                            movie_year = blocked_year + 1
                        else:
                            blocked_page = blocked_page + 1
                            movie_year = blocked_year

                        cursor.execute(
                            "INSERT INTO movie_by_page (value1, value2, value3, json_data) VALUES (%s, %s, %s, NULL)",
                            (
                                movie_year,
                                blocked_page,
                                worker_name,
                            ),
                        )
                        conn.commit()
                        cursor.close()
                else:
                    movie_year = blocked_year

                params["primary_release_year"] = movie_year
                params["page"] = blocked_page

                # API Request to Movie website
                response = requests.get(discover_endpoint, params=params)
                data = response.json()
                total_results = data.get("total_results", 0)
                total_pages = data.get("total_pages", 0)
                movie_counts.append(total_results)
                if movie_year % 1 == 0:
                    logging.info(
                        f"Movies at {movie_year} year, current page: {blocked_page} total pages: {total_pages} total number: {total_results}"
                    )
                save_movie_object(movie_year, blocked_page, data)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE movie_by_page SET json_data = %s WHERE value1 = %s AND value2 = %s ;",
                    (
                        json.dumps(data),
                        str(movie_year),
                        str(blocked_page),
                    ),
                )
                conn.commit()
                cursor.close()

                time.sleep(waiting_for_apicall)
                if movie_year == movie_to_year:
                    break
            except Exception as e:
                logging.critical(f"Error in getting data: {e}")
                if cursor.closed is False:
                    conn.rollback()
                time.sleep(3)

        logging.info(f"The data was get to last year: {movie_to_year}")
        # all data in table, so we need to wait and reload all data again
        logging.info(f"Waiting for {waiting_for_reload} secs to reload...")
        time.sleep(waiting_for_reload)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movie_by_page;")
        conn.commit()
        conn.close()

    except Exception as e:
        logging.critical(f"Error operation with database: {e}")
        time.sleep(5)
