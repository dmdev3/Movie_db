def create_db_objects(conn):
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
        CREATE TABLE IF NOT EXISTS movie_with_attr_total (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENTmovie_by_page_TIMESTAMP,
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
        CREATE TABLE IF NOT EXISTS movie_by_page (
            id SERIAL PRIMARY KEY
            , created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , value1 text
            , value2 text
            , value3 text
            , json_data JSONB
            , UNIQUE (value1, value2)            
        );
        CREATE OR REPLACE VIEW movie_count_per_year_by_page
            AS
            SELECT DISTINCT value1::integer AS movieyear,
                    (json_data -> 'total_results'::text)::integer AS moviecount
            FROM movie_by_page
            WHERE 1 = 1 AND value1::integer > 1900 AND (json_data -> 'total_results'::text) IS NOT NULL
            ORDER BY (value1::integer);
        CREATE TABLE IF NOT EXISTS movie_data (
            id SERIAL PRIMARY KEY
            , created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , value1 text
            , value2 text        
            , json_data JSONB            
        );
        CREATE INDEX values_idx ON movie_data (value1, value2);
    """
    )
    conn.commit()
    cursor.close()
