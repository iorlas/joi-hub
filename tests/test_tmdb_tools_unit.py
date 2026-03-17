from unittest.mock import MagicMock, patch

import pytest

from mcps.servers.tmdb import (
    GenreList,
    MediaList,
    MovieList,
    _fetch_alt_titles,
    discover_movies,
    list_genres,
    search_media,
)

MOVIE_DATA = {
    "id": 550,
    "title": "Fight Club",
    "original_title": "Fight Club",
    "overview": "An insomniac office worker...",
    "release_date": "1999-10-15",
    "popularity": 61.4,
    "vote_average": 8.4,
    "vote_count": 1000,
    "adult": False,
    "video": False,
    "genre_ids": [18],
    "original_language": "en",
}

TV_DATA = {
    "id": 1396,
    "name": "Breaking Bad",
    "original_name": "Breaking Bad",
    "overview": "A high school chemistry teacher...",
    "first_air_date": "2008-01-20",
    "popularity": 200.0,
    "vote_average": 8.9,
    "vote_count": 5000,
    "adult": False,
    "genre_ids": [18, 80],
    "original_language": "en",
    "origin_country": ["US"],
}


@pytest.mark.unit
class TestFetchAltTitles:
    @patch("mcps.servers.tmdb.tmdb")
    def test_movie_alt_titles(self, mock_tmdb):
        mock_movies = MagicMock()
        mock_movies.alternative_titles.return_value = {
            "titles": [
                {"iso_3166_1": "RU", "title": "Бойцовский клуб"},
                {"iso_3166_1": "DE", "title": "Fight Club"},
            ]
        }
        mock_tmdb.Movies.return_value = mock_movies

        result = _fetch_alt_titles("movie", 550)

        mock_tmdb.Movies.assert_called_once_with(550)
        mock_movies.alternative_titles.assert_called_once()
        assert result == {"RU": "Бойцовский клуб", "DE": "Fight Club"}

    @patch("mcps.servers.tmdb.tmdb")
    def test_tv_alt_titles(self, mock_tmdb):
        mock_tv = MagicMock()
        mock_tv.alternative_titles.return_value = {
            "results": [
                {"iso_3166_1": "RU", "title": "Во все тяжкие"},
            ]
        }
        mock_tmdb.TV.return_value = mock_tv

        result = _fetch_alt_titles("tv", 1396)

        mock_tmdb.TV.assert_called_once_with(1396)
        mock_tv.alternative_titles.assert_called_once()
        assert result == {"RU": "Во все тяжкие"}


@pytest.mark.unit
class TestSearchMedia:
    @patch("mcps.servers.tmdb.tmdb")
    def test_search_movie_only(self, mock_tmdb):
        mock_search = MagicMock()
        mock_search.movie.return_value = {"results": [MOVIE_DATA]}
        mock_tmdb.Search.return_value = mock_search

        result = search_media(query="Fight Club", media_type="movie")

        assert isinstance(result, MediaList)
        assert result.total == 1
        assert result.results[0].title == "Fight Club"
        assert result.results[0].media_type == "movie"
        mock_search.movie.assert_called_once_with(query="Fight Club", year=None)
        mock_search.tv.assert_not_called()

    @patch("mcps.servers.tmdb.tmdb")
    def test_search_tv_only(self, mock_tmdb):
        mock_search = MagicMock()
        mock_search.tv.return_value = {"results": [TV_DATA]}
        mock_tmdb.Search.return_value = mock_search

        result = search_media(query="Breaking Bad", media_type="tv")

        assert isinstance(result, MediaList)
        assert result.total == 1
        assert result.results[0].title == "Breaking Bad"
        assert result.results[0].media_type == "tv"
        mock_search.tv.assert_called_once_with(query="Breaking Bad")
        mock_search.movie.assert_not_called()

    @patch("mcps.servers.tmdb.tmdb")
    def test_search_both_types(self, mock_tmdb):
        mock_search = MagicMock()
        mock_search.movie.return_value = {"results": [MOVIE_DATA]}
        mock_search.tv.return_value = {"results": [TV_DATA]}
        mock_tmdb.Search.return_value = mock_search

        result = search_media(query="test")

        assert isinstance(result, MediaList)
        assert result.total == 2
        types = {r.media_type for r in result.results}
        assert types == {"movie", "tv"}

    @patch("mcps.servers.tmdb.tmdb")
    @patch("mcps.servers.tmdb._fetch_alt_titles")
    def test_search_by_imdb_id(self, mock_alt_titles, mock_tmdb):
        mock_find = MagicMock()
        mock_find.info.return_value = {
            "movie_results": [MOVIE_DATA],
            "tv_results": [],
        }
        mock_tmdb.Find.return_value = mock_find
        mock_alt_titles.return_value = {"RU": "Бойцовский клуб"}

        result = search_media(imdb_id="tt0137523")

        mock_tmdb.Find.assert_called_once_with("tt0137523")
        mock_find.info.assert_called_once_with(external_source="imdb_id")
        mock_alt_titles.assert_called_once_with("movie", 550)
        assert result.total == 1
        assert result.results[0].title == "Fight Club"
        assert result.results[0].alt_titles == {"RU": "Бойцовский клуб"}

    @patch("mcps.servers.tmdb.tmdb")
    @patch("mcps.servers.tmdb._fetch_alt_titles")
    def test_search_by_imdb_id_tv(self, mock_alt_titles, mock_tmdb):
        mock_find = MagicMock()
        mock_find.info.return_value = {
            "movie_results": [],
            "tv_results": [TV_DATA],
        }
        mock_tmdb.Find.return_value = mock_find
        mock_alt_titles.return_value = {"RU": "Во все тяжкие"}

        result = search_media(imdb_id="tt0903747")

        mock_alt_titles.assert_called_once_with("tv", 1396)
        assert result.total == 1
        assert result.results[0].media_type == "tv"

    def test_search_raises_without_query_or_imdb_id(self):
        with pytest.raises(ValueError, match="Provide query or imdb_id"):
            search_media()


@pytest.mark.unit
class TestDiscoverMovies:
    @patch("mcps.servers.tmdb.tmdb")
    def test_recommendations(self, mock_tmdb):
        mock_movie = MagicMock()
        mock_movie.recommendations.return_value = {"results": [MOVIE_DATA]}
        mock_tmdb.Movies.return_value = mock_movie

        result = discover_movies(source="recommendations", movie_id=550)

        assert isinstance(result, MovieList)
        mock_tmdb.Movies.assert_called_once_with(550)
        mock_movie.recommendations.assert_called_once()
        assert result.total == 1
        assert result.movies[0].title == "Fight Club"

    @patch("mcps.servers.tmdb.tmdb")
    def test_similar(self, mock_tmdb):
        mock_movie = MagicMock()
        mock_movie.similar_movies.return_value = {"results": [MOVIE_DATA]}
        mock_tmdb.Movies.return_value = mock_movie

        result = discover_movies(source="similar", movie_id=550)

        assert isinstance(result, MovieList)
        mock_movie.similar_movies.assert_called_once()
        assert result.total == 1

    @patch("mcps.servers.tmdb.tmdb")
    def test_genre(self, mock_tmdb):
        mock_discover = MagicMock()
        mock_discover.movie.return_value = {"results": [MOVIE_DATA]}
        mock_tmdb.Discover.return_value = mock_discover

        result = discover_movies(source="genre", genre_id=18, page=2)

        assert isinstance(result, MovieList)
        mock_discover.movie.assert_called_once_with(with_genres=18, page=2)
        assert result.total == 1

    def test_recommendations_raises_without_movie_id(self):
        with pytest.raises(ValueError, match="movie_id required"):
            discover_movies(source="recommendations")

    def test_similar_raises_without_movie_id(self):
        with pytest.raises(ValueError, match="movie_id required"):
            discover_movies(source="similar")

    def test_genre_raises_without_genre_id(self):
        with pytest.raises(ValueError, match="genre_id required"):
            discover_movies(source="genre")


@pytest.mark.unit
class TestListGenres:
    @patch("mcps.servers.tmdb.tmdb")
    def test_list_genres(self, mock_tmdb):
        mock_genres = MagicMock()
        mock_genres.movie_list.return_value = {
            "genres": [
                {"id": 28, "name": "Action"},
                {"id": 18, "name": "Drama"},
                {"id": 80, "name": "Crime"},
            ]
        }
        mock_tmdb.Genres.return_value = mock_genres

        result = list_genres()

        assert isinstance(result, GenreList)
        mock_tmdb.Genres.assert_called_once()
        mock_genres.movie_list.assert_called_once()
        assert result.total == 3
        assert result.offset == 0
        assert result.genres[0].name == "Action"
