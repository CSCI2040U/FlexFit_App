from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy base and engine setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    try:
        db = SessionLocal()
        print("✅ Database session started.")
        yield db
    except Exception as e:
        print(f"🚨 Database session error: {e}")
    finally:
        db.close()
        print("✅ Database session closed.")

# Create all tables
def create_db():
    Base.metadata.create_all(bind=engine)

# ✅ Schema for exercise creation (used in endpoints)
class ExerciseCreate(BaseModel):
    name: str
    description: str
    toughness: str
    media_url: str = None
    tags: List[str] = []
    suggested_reps: int

    class Config:
        from_attributes = True

# ✅ Helper function to fetch user data
def get_user_data(db: Session, user_id: int):
    from backend.models import User  # ✅ Imported only here to avoid circular import
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return {
            "id": user.id,
            "username": user.username or "",
            "full_name": user.full_name or "",
            "email": user.email or "",
            "height": user.height or "N/A",
            "weight": user.weight or "N/A",
            "gender": user.gender or "N/A",
            "dob": str(user.dob) if user.dob else "N/A",
            "role": user.role or "user"
        }
    return None

# ✅ Exercise fetch helpers
def get_exercise_by_id(db: Session, exercise_id: int):
    from backend.models import Exercise
    return db.query(Exercise).filter(Exercise.id == exercise_id).first()

def get_exercise_by_tag(db: Session, exercise_tag: str):
    from backend.models import Exercise
    return db.query(Exercise).filter(Exercise.tags == exercise_tag).first()

def get_exercise_by_toughness(db: Session, exercise_toughness: str):
    from backend.models import Exercise
    return db.query(Exercise).filter(Exercise.toughness == exercise_toughness).first()

# ✅ For direct CLI table creation
if __name__ == "__main__":
    create_db()
