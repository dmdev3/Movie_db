import logging
import time
import datetime
import requests
import json
import psycopg2
import uuid
import settings

genre_list = [
    [35, "Comedy"],
    [99, "Documentary"],
    [27, "Horror"],
    [28, "Action"],
    [80, "Crime"],
    [18, "Drama"],
    [10752, "War"],
    [37, "Western"],
]

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
    "with_genres": 12,
    "page": 1,  # Page number (adjust as needed)
    "language": "en-US",  # Language for results
}

# Створення списку для зберігання кількості фільмів за кожний рік та жанр
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
        # Створити об'єкт курсора
        cursor = conn.cursor()

        # Створити таблицю, якщо вона не існує
        cursor.execute(
            """

            CREATE TABLE IF NOT EXISTS movie_with_attr_total (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                value1 text,
                value2 text,
                value3 text,
                json_data JSONB,
                UNIQUE (value1, value2)
            );

            CREATE OR REPLACE VIEW movie_with_attr_total_per_year
                 AS
                 SELECT id,
                    value1::integer AS movieyear,
                    value2::integer AS moviegenre,
                    (json_data -> 'total_results'::text)::integer AS moviecount
                   FROM movie_with_attr_total
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
                    "SELECT "
                    " CAST(value1 AS INT) as movieyear"
                    " ,CAST(value2 AS INT) as movieyear"
                    " ,CASE WHEN CURRENT_TIMESTAMP - created_at > INTERVAL '2 minutes' AND json_data IS NULL THEN 1 ELSE 0 END AS LostRecords"
                    " FROM movie_with_attr_total"
                    " ORDER BY LostRecords DESC, value1 DESC, value2 DESC"
                    " LIMIT 1"
                )
                result = cursor.fetchall()

                # Define start_year
                if len(result) == 0:
                    blocked_year = movie_since_year - 1
                    blocked_genre_id = -1
                    blocked_flag = 0
                else:
                    blocked_year = result[0][0]
                    blocked_genre_id = result[0][1]
                    blocked_flag = result[0][2]

                if blocked_flag == 0:
                    if (
                        blocked_year == movie_to_year
                        and blocked_genre_id == len(genre_list) - 1
                    ):
                        # data was loaded we can finish the process
                        break
                    else:
                        # continue loading process from existing year, gener + 1
                        if blocked_genre_id == len(genre_list) - 1:
                            blocked_genre_id = 0
                            movie_year = blocked_year + 1
                        else:
                            blocked_genre_id = blocked_genre_id + 1
                            movie_year = blocked_year

                        cursor.execute(
                            "INSERT INTO movie_with_attr_total (value1, value2, value3, json_data) VALUES (%s, %s, %s, NULL)",
                            (
                                movie_year,
                                blocked_genre_id,
                                worker_name,
                            ),
                        )
                        conn.commit()
                        cursor.close()
                else:
                    movie_year = blocked_year

                params["primary_release_year"] = movie_year
                params["with_genres"] = genre_list[blocked_genre_id][0]

                # Запит для фільмів загального списку
                response = requests.get(discover_endpoint, params=params)
                data = response.json()
                total_results = data.get("total_results", 0)
                movie_counts.append(total_results)
                if movie_year % 1 == 0:
                    logging.info(
                        f"Total number of {genre_list[blocked_genre_id][1]} movies in {movie_year} year: {total_results}"
                    )
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE movie_with_attr_total SET json_data = %s WHERE value1 = %s AND value2 = %s ;",
                    (
                        json.dumps(data),
                        str(movie_year),
                        str(blocked_genre_id),
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
        cursor.execute("DELETE FROM movie_with_attr_total;")
        conn.commit()
        conn.close()

    except Exception as e:
        logging.critical(f"Error operation with database: {e}")
        time.sleep(5)
