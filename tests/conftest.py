import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEST_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/lumen_cv_test"
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)

assert (make_url(TEST_DATABASE_URL).database or "").endswith("_test"), (
    f"TEST_DATABASE_URL must name a database ending in '_test', got {TEST_DATABASE_URL!r}"
)

# server.config reads DATABASE_URL when server.* is first imported, so this must run before any server import.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


@pytest.fixture(scope="session")
def alembic_config() -> Config:
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "server" / "migrations"))
    return config


@pytest.fixture(scope="session")
def engine(alembic_config: Config) -> Iterator[Engine]:
    test_engine = create_engine(TEST_DATABASE_URL)
    try:
        with test_engine.connect():
            pass
    except OperationalError as exc:
        pytest.fail(
            f"Postgres is not reachable at {TEST_DATABASE_URL}: {exc.orig}\n"
            "Start it, then create the test database with: "
            "docker exec lumen-cv-postgres createdb -U postgres lumen_cv_test",
            pytrace=False,
        )

    command.upgrade(alembic_config, "head")
    yield test_engine
    test_engine.dispose()


@pytest.fixture(autouse=True)
def empty_database(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE users CASCADE"))


@pytest.fixture
def client() -> Iterator[TestClient]:
    from server.main import app

    with TestClient(app) as test_client:
        yield test_client
