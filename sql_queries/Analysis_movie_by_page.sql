SELECT id, created_at, value1, value2, value3

,(json_data -> 'total_pages'::text) AS totalpages
, json_data
	FROM public.movie_by_page
	WHERE 1=1
	and value2::int < 500
	--AND json_Data is null
	--AND (json_data -> 'total_pages'::text) IS NULL
	order by (case when json_Data is null then 1 else 0 end) desc, value1::int desc, value2::int desc
LIMIT 20
--	truncate table movie_by_page