import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, User, get_user_data

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the test database tables
Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    """Fixture to create a new database session for each test."""
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_user(db_session):
    """Fixture to create a fresh sample user each time."""
    db_session.query(User).delete()  # ✅ Clear previous test data
    db_session.commit()

    user = User(id=1, username="test", full_name="Test User", email="testuser@example.com",
                password_hash="hashed_pwd", height="5'9", weight="70kg", gender="Male", role="user")
    db_session.add(user)
    db_session.commit()

    return user


def test_create_user(db_session):
    """Test user creation and database insertion."""
    db_session.query(User).delete()  # ✅ Ensure clean state
    db_session.commit()

    new_user = User(id=1, username="test", full_name="Test User", email="testuser@example.com",
                    password_hash="hashed_pwd", height="5'9", weight="70kg", gender="Male", role="user")
    db_session.add(new_user)
    db_session.commit()

    fetched_user = db_session.query(User).filter(User.id == 1).first()
    assert fetched_user is not None
    assert fetched_user.username == "test"


def test_update_user(db_session, sample_user):
    """Test updating user details."""
    sample_user.height = "6'0"
    db_session.commit()

    updated_user = db_session.query(User).filter(User.id == 1).first()
    assert updated_user.height == "6'0"


def test_get_user_data(db_session, sample_user):
    """Test fetching user data by ID."""
    fetched_user = get_user_data(db_session, 1)
    assert fetched_user is not None
    assert fetched_user.username == "test"
