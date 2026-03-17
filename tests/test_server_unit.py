import pytest


@pytest.mark.unit
class TestServerImports:
    """Verify server module exports ASGI apps."""

    def test_jackett_app_exists(self):
        from mcps.server import jackett

        assert jackett is not None

    def test_transmission_app_exists(self):
        from mcps.server import transmission

        assert transmission is not None

    def test_tmdb_app_exists(self):
        from mcps.server import tmdb

        assert tmdb is not None

    def test_storage_app_exists(self):
        from mcps.server import storage

        assert storage is not None

    def test_apps_are_asgi_callable(self):
        from mcps.server import jackett, storage, tmdb, transmission

        # ASGI apps must be callable
        assert callable(jackett)
        assert callable(transmission)
        assert callable(tmdb)
        assert callable(storage)
