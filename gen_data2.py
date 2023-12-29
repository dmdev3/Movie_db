import logging
import time
import datetime
import requests
import json
import psycopg2
import uuid
import settings
import init_db as storage


def pulling_movie_resource(release_year: str):
    # Endpoint for discovering movies
    base_url = "https://api.themoviedb.org/3"
    discover_endpoint = f"{base_url}/discover/movie"
    # Parameters for the request
    params = {
        "api_key": settings.api_key,
        "sort_by": "original_title.asc",
        "primary_release_year": release_year,
        "page": 1,
        "language": "en-US",
    }
    try:
        # API Request to Movie website
        response = requests.get(discover_endpoint, params=params)
        if response.status_code != 200:
            raise RuntimeError("No data API call responses")
    except Exception:
        raise
    return response.json()


def db_cleanup_table(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movie_total_data;")
    conn.commit()
    cursor.close()


def db_add_data(conn, movie_year, movie_response_data):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE movie_total_data SET json_data = %s WHERE value1 = %s ;",
        (
            json.dumps(movie_response_data),
            str(movie_year),
        ),
    )
    conn.commit()
    cursor.close()
    pass


def get_param_for_request(conn, movie_since_year, movie_to_year, worker_name):
    try:
        # Get the last year
        cursor = conn.cursor()
        cursor.execute(
            "SELECT CAST(value1 AS INT) as movieyear"
            " ,CASE WHEN CURRENT_TIMESTAMP - created_at > INTERVAL '1 minutes' AND json_data IS NULL THEN 1 ELSE 0 END AS LostRecords"
            " FROM movie_total_data "
            " ORDER BY LostRecords DESC, value1 DESC LIMIT 1"
        )
        result = cursor.fetchall()

        # Define start_year
        if len(result) == 0:
            movie_year = movie_since_year - 1
            blocked_flag = 0
        else:
            movie_year = result[0][0]
            blocked_flag = result[0][1]

        if blocked_flag == 0:
            if movie_year < movie_to_year:
                # continue loading process from existing year + 1
                movie_year = movie_year + 1
                cursor.execute(
                    "INSERT INTO movie_total_data (value1, value2, json_data) VALUES (%s, %s, NULL)",
                    (
                        movie_year,
                        worker_name,
                    ),
                )
                conn.commit()
                cursor.close()
        return movie_year
    except Exception:
        if cursor.closed is False:
            conn.rollback()
        raise


def main():
    worker_name = str(uuid.uuid4())

    movie_since_year = settings.gen_data_movie_since_year
    movie_to_year = int(datetime.date.today().year)

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

            # Getting data
            movie_year = movie_since_year
            while movie_year < movie_to_year:
                try:
                    movie_year = get_param_for_request(
                        conn, movie_since_year, movie_to_year, worker_name
                    )

                    # Pulling info from movie res by API
                    movie_response_data = pulling_movie_resource(movie_year)

                    total_results = movie_response_data.get("total_results", 0)
                    if movie_year % 1 == 0:
                        logging.info(
                            f"Total number of movies in {movie_year} year: {total_results}"
                        )

                    db_add_data(conn, movie_year, movie_response_data)
                    time.sleep(settings.gen_data_waiting_for_apicall)

                except Exception as e:
                    logging.critical(f"Error in getting data: {e}")
                    time.sleep(settings.gen_data_waiting_for_apicall_on_error)

            logging.info(f"The data was get to last year: {movie_to_year}")
            # all data in table, so we need to wait and reload all data again
            logging.info(
                f"Waiting for {settings.gen_data_waiting_for_reload} secs to reload..."
            )
            time.sleep(settings.gen_data_waiting_for_reload)
            db_cleanup_table(conn)
            conn.close()

        except Exception as e:
            logging.critical(f"Error operation with database: {e}")
            time.sleep(settings.gen_data_waiting_for_reload)


if __name__ == "__main__":
    main()
