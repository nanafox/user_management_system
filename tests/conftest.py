import subprocess

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ums import models, schemas
from ums.api.main import app
from ums.config import settings
from ums.crud import crud_user
from ums.database import Base, get_db


@pytest.fixture(scope="package", autouse=True)
def setup_teardown_test_db():
    """Performs setup and teardown for the test database."""
    print("Setting up")
    subprocess.run(["./setup_test_db.sh"])

    yield

    print("Tearing down")
    subprocess.run(["./teardown_test_db.sh"])


@pytest.fixture
def session():
    """Sets up the session for the test database connection."""
    SQLALCHEMY_DATABASE_URL = (
        "postgresql://"
        f"{settings.db_user}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/{settings.db_name}_test"
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestDBSession = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestDBSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
async def api_client(session: Session):
    """Yields a client object to be used for API testing."""

    def override_get_db():
        """
        A fixture to override the default database session used in tests.

        Explanation:
        This fixture yields the provided session for testing purposes and
        ensures that the session is properly closed after the test.

        Returns:
            The database session for testing.
        """
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield AsyncClient(
        base_url="http://testserver", transport=ASGITransport(app=app)
    )


@pytest.fixture
def create_jdoe_user(session: Session) -> models.User:
    """
    Fixture to create a user with username 'jdoe' and password 'my_password'
    in the database.

    This fixture creates a user with specific credentials in the database
    using the provided session.

    Args:
        session (Session): The database session to use for creating the user.

    Returns:
        models.User: The created user object in the database.
    """
    user = schemas.UserCreate(username="jdoe", password="my_password")
    return crud_user.create(db=session, schema=user)
