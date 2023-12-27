INSERT INTO movies (adult, backdrop_path, genre_ids, original_language, original_title, overview, popularity, poster_path, release_date, title, video, vote_average, vote_count)
SELECT 
    json_data->>'adult'::boolean,
    json_data->>'backdrop_path',
    (json_data->>'genre_ids')::integer[],
    json_data->>'original_language',
    json_data->>'original_title',
    json_data->>'overview',
    (json_data->>'popularity')::numeric,
    json_data->>'poster_path',
    (json_data->>'release_date')::date,
    json_data->>'title',
    json_data->>'video'::boolean,
    (json_data->>'vote_average')::numeric,
    (json_data->>'vote_count')::integer
--FROM jsonb_file('C:\Training\Jupyter\jnotebook1\all_movies_tmdb_sample.json') AS json_data;
FROM jsonb_array_elements_text(pg_read_file('C:\Training\Jupyter\jnotebook1\all_movies_tmdb_sample.json')) AS json_data;



SELECT * FROM pg_read_file('/home/data/all_movies_tmdb_sample_f1.json')
SELECT * FROM pg_read_file('/home/data/all_movies_tmdb_sample_f1_r2.json')
INSERT INTO T2_JSONB(jsonb_data)
select * from json_array_elements_text('["foo", "bar"]')::jsonb
SELECT * FROM jsonb_array_elements_text(pg_read_file('/home/data/all_movies_tmdb_sample_f1.json'))
SELECT * FROM jsonb_array_elements(pg_read_file('/home/data/all_movies_tmdb_sample_f1_r2.json'))


INSERT INTO T2_JSONB(jsonb_data)

SELECT * FROM json_array_elements_text
INSERT INTO T2_JSONB(jsonb_data)
VALUES
('
[
  {
    "adult": false,
    "backdrop_path": null,
    "genre_ids": [
      99
    ],
    "id": 1206164,
    "original_language": "en",
    "original_title": "The  Making of Chronicles of a Lost Star",
    "overview": "Chronicles of a Lost Star has been a longwinded effort of two years. Follow along the story of the album''s creation from start to finish with behind the scenes footage, band interviews, the recording and mastering process, and more.",
    "popularity": 0.6,
    "poster_path": "/hne8wvPyO2cFd6CFcZdtTC5ecsW.jpg",
    "release_date": "2022-10-21",
    "title": "The  Making of Chronicles of a Lost Star",
    "video": false,
    "vote_average": 10,
    "vote_count": 1
  },
  {
    "adult": false,
    "backdrop_path": "/tWvGAA7g2DH2fHNdIAB646Gt5gh.jpg",
    "genre_ids": [
      16,
      53
    ],
    "id": 1099640,
    "original_language": "en",
    "original_title": "!",
    "overview": "Follows the rising panic of having something to get done, but being unable to make yourself start.",
    "popularity": 0.698,
    "poster_path": "/4HYQ1haWir4cljNfDTI5YEmdFdy.jpg",
    "release_date": "2023-03-24",
    "title": "!",
    "video": false,
    "vote_average": 0,
    "vote_count": 0
  }
  ]						   
									   '
	
	) as js

	
