import pytest
from rich.jupyter import display
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, Exercise, get_exercise_by_id, get_exercise_by_toughness

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
def sample_exercise():
    """Fixture to create a sample exercise."""
    return Exercise(id=1, name="Push-ups", description="Bodyweight exercise", toughness="Medium", suggested_reps=20)


def test_create_exercise(db_session, sample_exercise):
    """Test exercise creation and database insertion."""
    db_session.add(sample_exercise)
    db_session.commit()

    fetched_exercise = db_session.query(Exercise).filter(Exercise.id == 1).first()
    assert fetched_exercise is not None
    assert fetched_exercise.name == "Push-ups"
    assert fetched_exercise.toughness == "Medium"


def test_update_exercise(db_session, sample_exercise):
    """Test updating an exercise."""
    sample_exercise.suggested_reps = 30
    db_session.commit()

    updated_exercise = db_session.query(Exercise).filter(Exercise.id == 1).first()
    assert updated_exercise.suggested_reps == 20


def test_get_exercise_by_id(db_session, sample_exercise):
    """Test fetching exercise data by ID."""
    fetched_exercise = get_exercise_by_id(db_session, 1)
    assert fetched_exercise is not None
    assert fetched_exercise.name == "Push-ups"

def test_get_exercise_by_toughness(db_session, sample_exercise):
    fetched_exercise = get_exercise_by_toughness(db_session, "Medium")
    assert fetched_exercise is not None
    assert fetched_exercise.name == "Push-ups"