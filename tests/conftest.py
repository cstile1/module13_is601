# tests/conftest.py

import time
import logging
from typing import Generator, Dict, List
from contextlib import contextmanager

import pytest
from faker import Faker
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import Base, get_engine, get_sessionmaker
from app.models.user import User
from app.config import settings

# =============================================================================
# Logging
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# =============================================================================
# TEST DATABASE (SQLite)
# =============================================================================
fake = Faker()
Faker.seed(12345)

TEST_DATABASE_URL = settings.TEST_DATABASE_URL   # sqlite:///./test.db

# Create SQLite engine
test_engine = get_engine(TEST_DATABASE_URL)
TestingSessionLocal = get_sessionmaker(test_engine)


# =============================================================================
# Fake data helper
# =============================================================================
def create_fake_user() -> Dict[str, str]:
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "username": fake.unique.user_name(),
        "password": fake.password(length=12),
    }


@contextmanager
def managed_db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# =============================================================================
# Test database setup
# =============================================================================
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Drop & recreate database tables once per test session.
    Always uses SQLite, NOT PostgreSQL.
    """
    logger.info("Setting up TEST DATABASE with SQLite")

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    logger.info("Tearing down TEST DATABASE")
    Base.metadata.drop_all(bind=test_engine)


# =============================================================================
# Per-test database session
# =============================================================================
@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """
    Creates a new SQLite session for each test.
    Tables are truncated after every test for isolation.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        logger.info("Truncating tables after test...")
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


# =============================================================================
# Fake data fixtures
# =============================================================================
@pytest.fixture
def fake_user_data() -> Dict[str, str]:
    return create_fake_user()


@pytest.fixture
def test_user(db_session: Session) -> User:
    user_data = create_fake_user()
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def seed_users(db_session: Session, request) -> List[User]:
    try:
        num_users = request.param
    except AttributeError:
        num_users = 5

    users = []
    for _ in range(num_users):
        u = User(**create_fake_user())
        users.append(u)
        db_session.add(u)

    db_session.commit()
    return users


# =============================================================================
# Pytest options
# =============================================================================
def pytest_addoption(parser):
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="run tests marked slow"
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="use --run-slow to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
# ======================================================================================
# Playwright Fixtures for E2E Tests
# ======================================================================================
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_context():
    """
    Provide a Playwright browser context for UI tests.
    Installed by GitHub Actions via `playwright install`.
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True
        )
        try:
            yield context
        finally:
            context.close()
            browser.close()


@pytest.fixture
def page(browser_context):
    """
    Provide a fresh page object for each E2E test.
    """
    page = browser_context.new_page()
    try:
        yield page
    finally:
        page.close()
# ======================================================================================
# FastAPI Test Server Fixture (for E2E tests)
# ======================================================================================
import subprocess
import time
import requests
import pytest

def wait_for_server(url: str, timeout: int = 30):
    """Wait for FastAPI server to start."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

@pytest.fixture(scope="session")
def fastapi_server():
    """
    Start FastAPI server in background for E2E tests.
    """
    server_url = "http://127.0.0.1:8000/"

    # Start FastAPI app (main.py)
    process = subprocess.Popen(
        ["python", "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait until it is reachable
    if not wait_for_server(server_url, timeout=30):
        process.terminate()
        raise RuntimeError("FastAPI server failed to start for E2E tests")

    yield  # Tests run here

    # Cleanup
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
