import logging

import streamlit as st
import datetime
import pandas as pd
import psycopg2
import time
import matplotlib.pyplot as plt
import settings

# Get db params
db_user = settings.db_user
db_password = settings.db_password
db_host = settings.db_host
db_port = settings.db_port
db_name = settings.db_name


st.title("Movie Count Per Year v0.1")
chart_container0 = st.empty()
chart_container = st.empty()
# Set the initial X and Y axis ranges
initial_x_range = (settings.gen_data_movie_since_year, int(datetime.date.today().year))
initial_y_range = (0, 40000)

for i in range(1000):
    try:
        # Create a connection to the PostgreSQL database
        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_name,
        )

        # SQL query to retrieve data from the view
        query = (
            "SELECT "
            "movieyear::integer as movieyear, moviecount as moviecount "
            "FROM movie_count_per_year_by_page"
        )

        # Read data into a DataFrame
        df = pd.read_sql_query(query, con=conn)

        # Close the database connection

        # Get worker count
        worker_count = 0
        try:
            # Get the last year
            cursor = conn.cursor()
            cursor.execute(
                "SELECT count(distinct(value3)) as count_unique FROM movie_by_page;"
            )
            result = cursor.fetchall()
            cursor.close()
            # Define start_year
            if len(result) != 0:
                worker_count = result[0][0]

        except Exception as e:
            logging.critical(f"Error in getting worker count: {e}")
        conn.close()

        chart_container0.markdown(f"Worker Count: << {worker_count} >>")

        # Create a line chart using Matplotlib
        fig, ax = plt.subplots()
        ax.plot(df["movieyear"], df["moviecount"], label=f"Worker Count: {2}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Movie Count")
        ax.set_xlim(initial_x_range)
        ax.set_ylim(initial_y_range)

        chart_container.pyplot(fig)

        # Streamlit app
        # chart_container.line_chart(df.set_index('movieyear')['moviecount'])

        time.sleep(0)
    except Exception:
        chart_container.markdown("Дочекайтесь поки підніметься База даних.")
        time.sleep(1)
