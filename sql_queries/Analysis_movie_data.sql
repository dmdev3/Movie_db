SELECT id, created_at, value1, value2
,(json_data -> 'title'::text)::text AS movietitle
,(json_data -> 'release_date'::text)::text AS release_date
, json_data
	FROM public.movie_data
WHERE 1=1
--AND value1='1997'
order by value1::int desc, value2::int desc
LIMIT 100
	