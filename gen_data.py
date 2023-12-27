import logging
import time
import datetime
import requests
import json
import psycopg2
import uuid
import settings


worker_name = str(uuid.uuid4())

base_url = "https://api.themoviedb.org/3"
# Endpoint for discovering movies
discover_endpoint = f"{base_url}/discover/movie"

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
        cursor = conn.cursor()

        # Create tables in db
        cursor.execute(
            """

            CREATE TABLE IF NOT EXISTS movie_total_data (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                value1 text UNIQUE,
                value2 text,
                json_data JSONB
            );

            CREATE OR REPLACE VIEW public.movie_count_per_year
                 AS
                 SELECT id,
                    value1::integer AS movieyear,
                    (json_data -> 'total_results'::text)::integer AS moviecount
                   FROM movie_total_data
                  WHERE 1 = 1 AND value1::integer > 1900 AND json_data -> 'total_results' IS NOT NULL
                  ORDER BY movieyear;
        """
        )
        conn.commit()
        cursor.close()

        # Getting data block
        while True:
            try:
                # Get the last year
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT CAST(value1 AS INT) as movieyear"
                    " ,CASE WHEN CURRENT_TIMESTAMP - created_at > INTERVAL '20 minutes' AND json_data IS NULL THEN 1 ELSE 0 END AS LostRecords"
                    " FROM movie_total_data "
                    " ORDER BY LostRecords DESC, value1 DESC LIMIT 1"
                )
                result = cursor.fetchall()

                # Define start_year
                if len(result) == 0:
                    blocked_year = movie_since_year - 1
                    blocked_flag = 0
                else:
                    blocked_year = result[0][0]
                    blocked_flag = result[0][1]

                if blocked_flag == 0:
                    if blocked_year == movie_to_year:
                        # data was loaded we can finish the process
                        break
                    else:
                        # continue loading process from existing year + 1
                        movie_year = blocked_year + 1
                        cursor.execute(
                            "INSERT INTO movie_total_data (value1, value2, json_data) VALUES (%s, %s, NULL)",
                            (
                                movie_year,
                                worker_name,
                            ),
                        )
                        conn.commit()
                        cursor.close()
                else:
                    movie_year = blocked_year

                params["primary_release_year"] = movie_year

                # API Request to Movie website
                response = requests.get(discover_endpoint, params=params)
                data = response.json()
                total_results = data.get("total_results", 0)
                movie_counts.append(total_results)
                if movie_year % 1 == 0:
                    logging.info(
                        f"Total number of movies in {movie_year} year: {total_results}"
                    )
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE movie_total_data SET json_data = %s WHERE value1 = %s ;",
                    (
                        json.dumps(data),
                        str(movie_year),
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
        cursor.execute("DELETE FROM movie_total_data;")
        conn.commit()
        conn.close()

    except Exception as e:
        logging.critical(f"Error operation with database: {e}")
        time.sleep(5)
