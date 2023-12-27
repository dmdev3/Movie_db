import streamlit as st
import datetime
import pandas as pd
import psycopg2
import time
import matplotlib.pyplot as plt
import settings

# Завантажуємо змінні середовища з файлу .env

# Отримуємо значення змінних середовища
db_user = settings.db_user
db_password = settings.db_password
db_host = settings.db_host
db_port = settings.db_port
db_name = settings.db_name


# list of genre !! need to change
genre_list = [
    [35, "Comedy"],
    [99, "Documentary"],
    [27, "Horror"],
    [28, "Action"],
    [80, "Crime"],
    [18, "Drama"],
]


st.title("Movie By Genre Count Per Year v0.8.1")
chart_container = st.empty()
# Set the initial X and Y axis ranges
initial_x_range = (
    settings.gen_data_movie_since_year,
    int(datetime.date.today().year) + 1,
)
# initial_y_range = (0, 40000)
# initial_y_range = (0, 10000)
initial_y_range = (0, 7000)

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

        fig, ax = plt.subplots()
        for genre_id in range(len(genre_list)):
            # SQL query to retrieve data from the view
            query = (
                "SELECT "
                " movieyear::integer as movieyear, moviecount as moviecount"
                " FROM movie_with_attr_total_per_year"
                f" WHERE moviegenre = {genre_id};"
            )
            # Read data into a DataFrame
            df = pd.read_sql_query(query, con=conn)
            # Create a line chart using Matplotlib
            ax.plot(df["movieyear"], df["moviecount"], label=genre_list[genre_id][1])

        ax.set_xlabel("Year")
        ax.set_ylabel("Movie Count")
        ax.set_xlim(initial_x_range)
        ax.set_ylim(initial_y_range)
        ax.legend()

        chart_container.pyplot(fig)

        # Streamlit app
        # chart_container.line_chart(df.set_index('movieyear')['moviecount'])

        # Close the database connection
        conn.close()

        time.sleep(1)
    except Exception as err:
        chart_container.markdown("Дочекайтесь поки підніметься База даних.")
        chart_container.markdown(f"Error: {err}")
        time.sleep(1)
