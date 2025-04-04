import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from backend.database import Base, get_user_data
from backend.models import User, SavedExercise,Exercise


# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
# ✅ Add connect_args to enable SQLite foreign key support
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the test database tables
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()

    # ✅ Enables ON DELETE CASCADE in SQLite
    session.execute(text("PRAGMA foreign_keys=ON"))

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


# ✅ UT-01-CB: Test creating a user and retrieving them from the DB
def test_create_user(db_session):
    """Test ID: UT-01-CB - Create user and verify retrieval from DB."""
    db_session.query(User).delete()  # ✅ Ensure clean state
    db_session.commit()

    new_user = User(id=1, username="test", full_name="Test User", email="testuser@example.com",
                    password_hash="hashed_pwd", height="5'9", weight="70kg", gender="Male", role="user")
    db_session.add(new_user)
    db_session.commit()

    fetched_user = db_session.query(User).filter(User.id == 1).first()
    assert fetched_user is not None
    assert fetched_user.username == "test"


# ✅ UT-02-CB: Test updating user height
def test_update_user(db_session, sample_user):
    """Test ID: UT-02-CB - Update user height."""
    sample_user.height = "6'0"
    db_session.commit()

    updated_user = db_session.query(User).filter(User.id == 1).first()
    assert updated_user.height == "6'0"


# ✅ UT-03-CB: Test updating user weight
def test_update_user_weight(db_session, sample_user):
    """Test ID: UT-03-CB - Update user weight."""
    sample_user.weight = "90kg"
    db_session.commit()

    updated_user_weight = db_session.query(User).filter(User.id == 1).first()
    assert updated_user_weight.weight == "90kg"


# ✅ UT-04-CB: Test saving a new exercise to user profile
def test_updateuser_saved_exercises(db_session, sample_user):
    """Test ID: UT-04-CB - Save exercise for user."""

    # Create the exercise FIRST (foreign key needs this!)
    exercise = Exercise(id=101, name="Test Exercise", description="Desc", toughness="Easy", suggested_reps=10)
    db_session.add(exercise)
    db_session.commit()

    # Now create the saved link
    saved = SavedExercise(user_id=sample_user.id, exercise_id=exercise.id)
    db_session.add(saved)
    db_session.commit()

    # Check it exists
    result = db_session.query(SavedExercise).filter_by(user_id=sample_user.id, exercise_id=exercise.id).first()
    assert result is not None
    assert result.user_id == sample_user.id
    assert result.exercise_id == exercise.id



# ✅ UT-05-OB: Test getting user data from DB and verifying returned values
def test_get_user_data(db_session, sample_user):
    """Test ID: UT-05-OB - Fetch user data and validate returned values."""
    fetched_user = get_user_data(db_session, 1)
    assert fetched_user is not None
    assert fetched_user["username"] == "test"

# ✅ IT-01: Integration Test - Save an exercise for a user
def test_integration_user_saves_exercise(db_session, sample_user):
    """Test ID: IT-01 - Link user with an exercise via SavedExercise (User + Exercise)."""

    # ✅ Clear out any previous exercises or links
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.commit()

    # Create the exercise
    exercise = Exercise(id=101, name="Plank", description="Core exercise", toughness="Medium", suggested_reps=60)
    db_session.add(exercise)
    db_session.commit()

    # Save it to user
    saved = SavedExercise(user_id=sample_user.id, exercise_id=exercise.id)
    db_session.add(saved)
    db_session.commit()

    # Confirm it saved correctly
    result = db_session.query(SavedExercise).filter_by(user_id=sample_user.id, exercise_id=exercise.id).first()
    assert result is not None


# ✅ IT-02: Integration Test - Retrieve user and saved exercises
def test_integration_get_user_with_saved_exercises(db_session, sample_user):
    """Test ID: IT-02 - Retrieve a user along with their saved exercises."""
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.commit()

    # Create and add exercise
    exercise = Exercise(id=102, name="Jumping Jacks", description="Cardio warm-up", toughness="Easy", suggested_reps=30)
    db_session.add(exercise)
    db_session.commit()

    # Link exercise to user
    saved = SavedExercise(user_id=sample_user.id, exercise_id=exercise.id)
    db_session.add(saved)
    db_session.commit()

    # Query user and check related SavedExercises
    saved_exercises = db_session.query(SavedExercise).filter_by(user_id=sample_user.id).all()
    assert len(saved_exercises) > 0
    assert saved_exercises[0].exercise_id == exercise.id

# ✅ IT-03: Integration Test - User saves multiple exercises
def test_integration_user_saves_multiple_exercises(db_session, sample_user):
    """Test ID: IT-03 - Save and retrieve multiple exercises for a single user."""
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.commit()

    # Create multiple exercises
    ex1 = Exercise(id=201, name="Burpees", description="Full-body", toughness="Hard", suggested_reps=10)
    ex2 = Exercise(id=202, name="Lunges", description="Legs", toughness="Medium", suggested_reps=20)
    db_session.add_all([ex1, ex2])
    db_session.commit()

    # Link both exercises to the user
    saved1 = SavedExercise(user_id=sample_user.id, exercise_id=ex1.id)
    saved2 = SavedExercise(user_id=sample_user.id, exercise_id=ex2.id)
    db_session.add_all([saved1, saved2])
    db_session.commit()

    # Fetch and validate saved exercises
    results = db_session.query(SavedExercise).filter_by(user_id=sample_user.id).all()
    assert len(results) == 2
    assert {res.exercise_id for res in results} == {ex1.id, ex2.id}

# ✅ IT-04: Integration Test - Multiple users saving the same exercise
def test_integration_multiple_users_save_same_exercise(db_session, sample_user):
    """Test ID: IT-04 - Ensure multiple users can save the same exercise."""
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.commit()

    # Create another user
    user2 = User(id=2, username="second", full_name="Second User", email="second@example.com",
                 password_hash="pwd", height="6'0", weight="80kg", gender="Male", role="user")
    db_session.add(user2)
    db_session.commit()

    # Create a shared exercise
    exercise = Exercise(id=301, name="Mountain Climbers", description="Core & cardio", toughness="Hard", suggested_reps=25)
    db_session.add(exercise)
    db_session.commit()

    # Both users save the same exercise
    save1 = SavedExercise(user_id=sample_user.id, exercise_id=exercise.id)
    save2 = SavedExercise(user_id=user2.id, exercise_id=exercise.id)
    db_session.add_all([save1, save2])
    db_session.commit()

    # Check both saved entries exist
    saved_for_exercise = db_session.query(SavedExercise).filter_by(exercise_id=exercise.id).all()
    user_ids = {entry.user_id for entry in saved_for_exercise}

    assert len(saved_for_exercise) == 2
    assert sample_user.id in user_ids
    assert user2.id in user_ids

# ✅ IT-05: Integration Test - Fetch multiple exercises by toughness
def test_integration_get_exercises_by_toughness_multiple(db_session):
    """Test ID: IT-05 - Retrieve multiple exercises by shared toughness level."""
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.commit()

    # Create multiple exercises with the same toughness
    ex1 = Exercise(id=401, name="Push-ups", description="Upper body", toughness="Medium", suggested_reps=20)
    ex2 = Exercise(id=402, name="Squats", description="Lower body", toughness="Medium", suggested_reps=25)
    ex3 = Exercise(id=403, name="High Knees", description="Cardio", toughness="Easy", suggested_reps=40)
    db_session.add_all([ex1, ex2, ex3])
    db_session.commit()

    # Query for Medium toughness
    results = db_session.query(Exercise).filter_by(toughness="Medium").all()

    # Verify the correct number and contents
    assert len(results) == 2
    names = {e.name for e in results}
    assert "Push-ups" in names
    assert "Squats" in names

# ✅ IT-06: Integration Test - Verify specific saved exercise exists for user
def test_integration_check_specific_saved_exercise(db_session, sample_user):
    """Test ID: IT-06 - Check if a specific saved exercise exists for a user."""
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.commit()

    # Create and add an exercise
    exercise = Exercise(id=501, name="Sit-ups", description="Core", toughness="Easy", suggested_reps=30)
    db_session.add(exercise)
    db_session.commit()

    # Save it for the user
    saved = SavedExercise(user_id=sample_user.id, exercise_id=exercise.id)
    db_session.add(saved)
    db_session.commit()

    # Check if the saved record exists
    exists = db_session.query(SavedExercise).filter_by(user_id=sample_user.id, exercise_id=exercise.id).first()

    assert exists is not None
    assert exists.exercise_id == 501

# ✅ IT-07: Integration Test - Exercise update reflects for user who saved it
def test_integration_updated_exercise_reflects_for_user(db_session, sample_user):
    """Test ID: IT-07 - Update an exercise and verify the changes reflect for user."""
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.commit()

    # Create and add exercise
    exercise = Exercise(id=601, name="Wall Sit", description="Static leg hold", toughness="Medium", suggested_reps=60)
    db_session.add(exercise)
    db_session.commit()

    # User saves the exercise
    saved = SavedExercise(user_id=sample_user.id, exercise_id=exercise.id)
    db_session.add(saved)
    db_session.commit()

    # Update the exercise toughness
    exercise.toughness = "Hard"
    db_session.commit()

    # Re-fetch and verify update reflects
    updated = db_session.query(Exercise).filter_by(id=exercise.id).first()
    assert updated.toughness == "Hard"

    # Also make sure the saved entry still exists and links correctly
    link = db_session.query(SavedExercise).filter_by(user_id=sample_user.id, exercise_id=exercise.id).first()
    assert link is not None
    assert link.exercise_id == updated.id

# ✅ IT-08: Integration Test - Delete saved exercise for user
def test_integration_delete_saved_exercise(db_session, sample_user):
    """Test ID: IT-08 - Remove a saved exercise and confirm it's deleted."""
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.commit()

    # Create and add an exercise
    exercise = Exercise(id=701, name="Toe Touches", description="Flexibility", toughness="Easy", suggested_reps=20)
    db_session.add(exercise)
    db_session.commit()

    # Save it for the user
    saved = SavedExercise(user_id=sample_user.id, exercise_id=exercise.id)
    db_session.add(saved)
    db_session.commit()

    # Delete the saved entry
    db_session.delete(saved)
    db_session.commit()

    # Confirm it's gone
    result = db_session.query(SavedExercise).filter_by(user_id=sample_user.id, exercise_id=exercise.id).first()
    assert result is None

# ✅ ST-01: System Test - User registers, adds exercise, and saves it
def test_system_full_user_workout_flow(db_session):
    """Test ID: ST-01 - Full flow: register user, add exercise, and save it."""

    # Clean state
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.query(User).delete()
    db_session.commit()

    # Register a user
    user = User(id=1, username="fituser", full_name="Fit User", email="fit@example.com",
                password_hash="secure123", height="5'8", weight="70kg", gender="Female", role="user")
    db_session.add(user)
    db_session.commit()

    # Add an exercise
    exercise = Exercise(id=801, name="Jump Rope", description="Cardio endurance", toughness="Medium", suggested_reps=50)
    db_session.add(exercise)
    db_session.commit()

    # Save it to user's profile
    saved = SavedExercise(user_id=user.id, exercise_id=exercise.id)
    db_session.add(saved)
    db_session.commit()

    # Final check: everything is linked properly
    result = db_session.query(SavedExercise).filter_by(user_id=user.id, exercise_id=exercise.id).first()
    assert result is not None
    assert result.user_id == user.id
    assert result.exercise_id == exercise.id

# ✅ ST-02: System Test - Save exercise and update user profile
def test_system_user_saves_exercise_then_updates_profile(db_session):
    """Test ID: ST-02 - User saves an exercise, then updates their profile."""

    # Clean DB
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.query(User).delete()
    db_session.commit()

    # Register user
    user = User(id=2, username="update_user", full_name="Updater", email="update@example.com",
                password_hash="pass123", height="5'7", weight="65kg", gender="Non-Binary", role="user")
    db_session.add(user)
    db_session.commit()

    # Add and save exercise
    exercise = Exercise(id=802, name="Box Jumps", description="Plyometric", toughness="Hard", suggested_reps=12)
    db_session.add(exercise)
    db_session.commit()

    saved = SavedExercise(user_id=user.id, exercise_id=exercise.id)
    db_session.add(saved)
    db_session.commit()

    # Update user profile
    user.height = "5'9"
    user.weight = "70kg"
    db_session.commit()

    # Verify both updates and relationship still exist
    updated_user = db_session.query(User).filter_by(id=user.id).first()
    assert updated_user.height == "5'9"
    assert updated_user.weight == "70kg"

    saved_entry = db_session.query(SavedExercise).filter_by(user_id=user.id, exercise_id=exercise.id).first()
    assert saved_entry is not None

# ✅ ST-03: System Test - Save multiple exercises, then delete one
def test_system_user_saves_and_deletes_one_exercise(db_session):
    """Test ID: ST-03 - User saves multiple exercises, then deletes one."""

    # Clean state
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.query(User).delete()
    db_session.commit()

    # Register user
    user = User(id=3, username="multi_user", full_name="Multi Save", email="multi@example.com",
                password_hash="abc123", height="5'6", weight="60kg", gender="Female", role="user")
    db_session.add(user)
    db_session.commit()

    # Create two exercises
    ex1 = Exercise(id=803, name="Rowing", description="Full body cardio", toughness="Medium", suggested_reps=100)
    ex2 = Exercise(id=804, name="Step-ups", description="Leg focus", toughness="Easy", suggested_reps=30)
    db_session.add_all([ex1, ex2])
    db_session.commit()

    # Save both exercises
    s1 = SavedExercise(user_id=user.id, exercise_id=ex1.id)
    s2 = SavedExercise(user_id=user.id, exercise_id=ex2.id)
    db_session.add_all([s1, s2])
    db_session.commit()

    # Delete one saved exercise
    db_session.delete(s1)
    db_session.commit()

    # Verify one deleted, one remains
    remaining = db_session.query(SavedExercise).filter_by(user_id=user.id).all()
    assert len(remaining) == 1
    assert remaining[0].exercise_id == ex2.id

# ✅ ST-04: System Test - Two users save different exercises and update profiles independently
def test_system_two_users_save_and_update_independently(db_session):
    """Test ID: ST-04 - Two users save different exercises and update their profiles independently."""

    # Clean DB
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.query(User).delete()
    db_session.commit()

    # Create two users
    user1 = User(id=4, username="userA", full_name="User A", email="a@example.com",
                 password_hash="a123", height="5'5", weight="55kg", gender="Male", role="user")
    user2 = User(id=5, username="userB", full_name="User B", email="b@example.com",
                 password_hash="b123", height="6'0", weight="80kg", gender="Female", role="user")
    db_session.add_all([user1, user2])
    db_session.commit()

    # Create two exercises
    ex1 = Exercise(id=805, name="Side Planks", description="Oblique hold", toughness="Medium", suggested_reps=30)
    ex2 = Exercise(id=806, name="Jump Squats", description="Explosive legs", toughness="Hard", suggested_reps=15)
    db_session.add_all([ex1, ex2])
    db_session.commit()

    # Each user saves a different exercise
    s1 = SavedExercise(user_id=user1.id, exercise_id=ex1.id)
    s2 = SavedExercise(user_id=user2.id, exercise_id=ex2.id)
    db_session.add_all([s1, s2])
    db_session.commit()

    # Users update their profile separately
    user1.weight = "58kg"
    user2.height = "5'11"
    db_session.commit()

    # Assertions
    updated_user1 = db_session.query(User).filter_by(id=user1.id).first()
    updated_user2 = db_session.query(User).filter_by(id=user2.id).first()
    assert updated_user1.weight == "58kg"
    assert updated_user2.height == "5'11"

    saved1 = db_session.query(SavedExercise).filter_by(user_id=user1.id, exercise_id=ex1.id).first()
    saved2 = db_session.query(SavedExercise).filter_by(user_id=user2.id, exercise_id=ex2.id).first()
    assert saved1 is not None
    assert saved2 is not None

# ✅ ST-05: System Test - User saves exercise, then exercise is updated
def test_system_user_sees_updated_exercise_info(db_session):
    """Test ID: ST-05 - Exercise is updated after being saved by user, and reflects correctly."""

    # Clean DB
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.query(User).delete()
    db_session.commit()

    # Register user
    user = User(id=6, username="reflect_user", full_name="Reflect Test", email="reflect@example.com",
                password_hash="xyz123", height="5'7", weight="68kg", gender="Female", role="user")
    db_session.add(user)
    db_session.commit()

    # Add exercise
    exercise = Exercise(id=807, name="Knee Push-ups", description="Beginner upper body", toughness="Easy", suggested_reps=10)
    db_session.add(exercise)
    db_session.commit()

    # Save it
    saved = SavedExercise(user_id=user.id, exercise_id=exercise.id)
    db_session.add(saved)
    db_session.commit()

    # Update exercise
    exercise.suggested_reps = 15
    db_session.commit()

    # Fetch and validate update reflects
    updated_exercise = db_session.query(Exercise).filter_by(id=exercise.id).first()
    assert updated_exercise.suggested_reps == 15

    # Confirm user still linked
    link = db_session.query(SavedExercise).filter_by(user_id=user.id, exercise_id=exercise.id).first()
    assert link is not None

# ✅ ST-06: System Test - User deletion removes saved data
def test_system_user_deletion_removes_saved_exercises(db_session):
    """Test ID: ST-06 - Deleting a user also removes their saved exercises."""

    # Clean DB
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.query(User).delete()
    db_session.commit()

    # Register user
    user = User(id=7, username="delete_user", full_name="Delete Me", email="delete@example.com",
                password_hash="del123", height="5'10", weight="75kg", gender="Male", role="user")
    db_session.add(user)
    db_session.commit()

    # Add exercise
    exercise = Exercise(id=808, name="Bird-Dogs", description="Back stability", toughness="Medium", suggested_reps=20)
    db_session.add(exercise)
    db_session.commit()

    # Save it
    saved = SavedExercise(user_id=user.id, exercise_id=exercise.id)
    db_session.add(saved)
    db_session.commit()

    # Delete user
    db_session.delete(user)
    db_session.commit()

    # Verify user's saved data is also gone
    remaining = db_session.query(SavedExercise).filter_by(user_id=user.id).all()
    assert len(remaining) == 0

# ✅ ST-07: System Test - Admin adds exercise, users can view it
def test_system_admin_adds_exercise_all_users_can_view(db_session):
    """Test ID: ST-07 - Admin creates an exercise, and it's visible to other users."""

    # Clean DB
    db_session.query(SavedExercise).delete()
    db_session.query(Exercise).delete()
    db_session.query(User).delete()
    db_session.commit()

    # Create admin and user
    admin = User(id=8, username="admin1", full_name="Admin One", email="admin@example.com",
                 password_hash="adminpass", height="N/A", weight="N/A", gender="N/A", role="admin")
    user = User(id=9, username="viewer", full_name="Regular User", email="user@example.com",
                password_hash="userpass", height="5'6", weight="60kg", gender="Female", role="user")
    db_session.add_all([admin, user])
    db_session.commit()

    # Admin adds a new exercise
    exercise = Exercise(id=809, name="Wall Ball", description="Explosive strength", toughness="Hard", suggested_reps=20)
    db_session.add(exercise)
    db_session.commit()

    # Regular user queries for it
    found = db_session.query(Exercise).filter_by(name="Wall Ball").first()

    assert found is not None
    assert found.toughness == "Hard"

# ✅ ST-08: System Test - Search exercises by tag
def test_system_user_searches_exercises_by_tag(db_session):
    """Test ID: ST-08 - User searches for exercises by a specific tag."""

    # Clean DB
    db_session.query(Exercise).delete()
    db_session.commit()

    # Create tagged exercises
    ex1 = Exercise(id=810, name="Jump Rope", description="Cardio", toughness="Medium", tags="cardio", suggested_reps=50)
    ex2 = Exercise(id=811, name="Deadlift", description="Strength", toughness="Hard", tags="strength", suggested_reps=5)
    ex3 = Exercise(id=812, name="Burpees", description="Cardio full-body", toughness="Hard", tags="cardio,full-body", suggested_reps=20)
    db_session.add_all([ex1, ex2, ex3])
    db_session.commit()

    # Simulate a user search by "cardio" tag
    results = db_session.query(Exercise).filter(Exercise.tags.like("%cardio%")).all()

    # Check that only cardio-tagged exercises are returned
    result_names = {e.name for e in results}
    assert "Jump Rope" in result_names
    assert "Burpees" in result_names
    assert "Deadlift" not in result_names

