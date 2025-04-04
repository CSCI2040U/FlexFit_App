import pytest
from rich.jupyter import display
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, get_exercise_by_id, get_exercise_by_toughness
from backend.models import Exercise
from backend.database import Base, get_user_data
from backend.models import User, SavedExercise

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


#  UT-06-CB: Test creating a new exercise and verifying insertion
def test_create_exercise(db_session, sample_exercise):
    """Test ID: UT-06-CB - Create a new exercise and verify it's added to the DB."""
    db_session.add(sample_exercise)
    db_session.commit()

    fetched_exercise = db_session.query(Exercise).filter(Exercise.id == 1).first()
    assert fetched_exercise is not None
    assert fetched_exercise.name == "Push-ups"
    assert fetched_exercise.toughness == "Medium"


#  UT-07-CB: Test updating an exercise's reps
def test_update_exercise(db_session, sample_exercise):
    """Test ID: UT-07-CB - Update exercise suggested reps and verify change."""
    db_session.add(sample_exercise)
    db_session.commit()

    sample_exercise.suggested_reps = 30
    db_session.commit()

    updated_exercise = db_session.query(Exercise).filter(Exercise.id == 1).first()
    assert updated_exercise.suggested_reps == 30


#  UT-08-OB: Test fetching an exercise by its ID
def test_get_exercise_by_id(db_session, sample_exercise):
    """Test ID: UT-08-OB - Fetch exercise by ID and validate returned data."""
    db_session.add(sample_exercise)
    db_session.commit()

    fetched_exercise = get_exercise_by_id(db_session, 1)
    assert fetched_exercise is not None
    assert fetched_exercise.name == "Push-ups"


#  UT-09-OB: Test fetching an exercise by toughness level
def test_get_exercise_by_toughness(db_session, sample_exercise):
    """Test ID: UT-09-OB - Fetch exercise by toughness and validate result."""
    db_session.add(sample_exercise)
    db_session.commit()

    fetched_exercise = get_exercise_by_toughness(db_session, "Medium")
    assert fetched_exercise is not None
    assert fetched_exercise.name == "Push-ups"
