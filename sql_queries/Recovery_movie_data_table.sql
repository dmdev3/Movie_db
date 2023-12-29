TRUNCATE TABLE movie_data;
INSERT INTO movie_data(created_at, value1, value2, json_data)
SELECT created_at, value1, value2, json_data from movie_data_bkp_dt20231228
--LIMIT 5


TRUNCATE TABLE movie_by_page;

INSERT INTO movie_by_page(created_at, value1, value2, value3, json_data)
SELECT created_at, value1, value2, value3, json_data 
FROM movie_by_page_bkp_dt20231228;

DELETE FROM movie_by_page WHERE value2::int>500;
--LIMIT 5
-- DELETE FROM movie_by_page WHERE value2::int>500
-- SELECT * FROM movie_by_page WHERE value2::int>500
--order by value2::int