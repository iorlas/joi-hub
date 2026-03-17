import os

from dotenv import load_dotenv

load_dotenv()

if not os.getenv("TMDB_API_KEY"):
    os.environ["TMDB_API_KEY"] = "dummy_key_for_vcr_replay"

import pytest
import tmdbsimple as tmdb

if not tmdb.API_KEY:
    tmdb.API_KEY = os.environ["TMDB_API_KEY"]


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": ["api_key"],
        "filter_headers": ["authorization", "x-transmission-session-id"],
        "record_mode": "once",
    }


@pytest.fixture(autouse=True)
def reset_transmission_client():
    import mcps.servers.transmission as tm

    tm._client = None
    yield
    tm._client = None


def pytest_addoption(parser):
    parser.addoption("--update-snapshots", action="store_true", help="Update golden snapshot files")


@pytest.fixture(scope="session")
def update_snapshots(request):
    return request.config.getoption("--update-snapshots")
