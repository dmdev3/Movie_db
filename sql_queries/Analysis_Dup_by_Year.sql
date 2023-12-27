SELECT CAST(value1 AS INT) as movieyear, count(1) as cnt
FROM movie_total_data 
GROUP BY value1

order by cnt desc, movieyear desc
LIMIT 90