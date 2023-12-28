SELECT value1::int
, count(distinct value2) as pages
, count(1) as Cnt_perYear
,(SELECT count(1) FROM movie_data) as TotalCnt

	FROM public.movie_data
	group by value1::int
order by value1::int desc
--, value2::int desc
-- select  2048 + 2139 +20 = 4207