import logging
import time
import datetime
import requests
import json
import psycopg2
import uuid
import settings
import init_db as storage


def pulling_movie_resource(release_year: str, genre: int):
    # Endpoint for discovering movies
    base_url = "https://api.themoviedb.org/3"
    discover_endpoint = f"{base_url}/discover/movie"

    # Parameters for the request
    params = {
        "api_key": settings.api_key,
        "sort_by": "original_title.asc",
        "primary_release_year": release_year,
        "with_genres": genre,
        "page": 1,  # Page number (adjust as needed)
        "language": "en-US",  # Language for results
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
    cursor.execute("DELETE FROM movie_with_attr_total;")
    conn.commit()
    cursor.close()


def db_add_data(conn, movie_year, blocked_genre_id, movie_response_data):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE movie_with_attr_total SET json_data = %s WHERE value1 = %s AND value2 = %s ;",
        (json.dumps(movie_response_data), str(movie_year), str(blocked_genre_id)),
    )
    conn.commit()
    cursor.close()
    pass


def get_param_for_request(
    conn, movie_since_year, movie_to_year, worker_name, list_end=False
):
    try:
        # Get the last year
        cursor = conn.cursor()
        cursor.execute(
            "SELECT "
            " CAST(value1 AS INT) as movieyear"
            " ,CAST(value2 AS INT) as moviegenreid"
            " ,CASE WHEN CURRENT_TIMESTAMP - created_at > INTERVAL '1 minutes' AND json_data IS NULL THEN 1 ELSE 0 END AS LostRecords"
            " FROM movie_with_attr_total"
            " ORDER BY LostRecords DESC, value1 DESC, value2 DESC"
            " LIMIT 1"
        )
        result = cursor.fetchall()

        # Define start_year
        if len(result) == 0:
            movie_year = movie_since_year
            blocked_genre_id = -1
            blocked_flag = 0
        else:
            movie_year = result[0][0]
            blocked_genre_id = result[0][1]
            blocked_flag = result[0][2]

        if blocked_flag == 0:
            if (
                movie_year == movie_to_year
                and blocked_genre_id == len(settings.genre_list) - 1
            ):
                # data was loaded, so we can finish the process
                list_end = True
            else:
                # continue loading process from existing year, gener + 1
                if blocked_genre_id == len(settings.genre_list) - 1:
                    blocked_genre_id = 0
                    movie_year += 1
                else:
                    blocked_genre_id += 1

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

        return movie_year, blocked_genre_id, list_end
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

            # Getting data block
            while True:
                try:
                    (
                        movie_year,
                        blocked_genre_id,
                        movie_finished_year,
                    ) = get_param_for_request(
                        conn,
                        movie_since_year,
                        movie_to_year,
                        worker_name,
                        list_end=False,
                    )
                    if movie_finished_year == True:
                        break

                    # Pulling info from movie res by API
                    movie_response_data = pulling_movie_resource(
                        movie_year, settings.genre_list[blocked_genre_id][0]
                    )

                    total_results = movie_response_data.get("total_results", 0)
                    logging.info(
                        f"Total number of {settings.genre_list[blocked_genre_id][1]} movies in {movie_year} year: {total_results}"
                    )
                    db_add_data(conn, movie_year, blocked_genre_id, movie_response_data)
                    time.sleep(settings.gen_data_waiting_for_apicall)

                except Exception as e:
                    logging.critical(f"Error in getting data: {e}")
                    time.sleep(settings.gen_data_waiting_for_apicall_on_error)

            logging.info(f"The data was got for the last year: {movie_to_year}")
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
