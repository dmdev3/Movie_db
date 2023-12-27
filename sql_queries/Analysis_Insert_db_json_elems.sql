-- Припустимо, що ваш файл має шлях '/повний/шлях/до/вашого/файлу.json'
-- та відповідає формату JSON з попереднього прикладу
INSERT INTO T2_JSONB (jsonb_data)
SELECT value::JSONB
FROM jsonb_array_elements_text(pg_read_file('/home/data/all_movies_tmdb_sample_f1_r2.json')) AS data;

INSERT INTO T2_JSONB (jsonb_data)
SELECT jsonb_populate_recordset(null::T2_JSONB, pg_read_file('/home/data/all_movies_tmdb_sample_f1_r2.json')::JSONB);

INSERT INTO T2_JSONB (jsonb_data)
SELECT pg_read_file('/home/data/all_movies_tmdb_sample_f1_r2.json')::JSONB;


INSERT INTO T2_JSONB (jsonb_data)
SELECT value::JSONB
FROM jsonb_array_elements_text('[
  {
    "adult": false,
    "backdrop_path": null,
    "genre_ids": [99],
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
    "genre_ids": [16, 53],
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
]') AS data;
