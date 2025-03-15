from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv  # Importing the dotenv module

# Load environment variables from the .env file
load_dotenv()

# Retrieve the DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")  # Get this from the .env file or environment

Base = declarative_base()

# Database engine setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    try:
        db = SessionLocal()
        print("✅ Database session started.")  # ✅ Debugging log
        yield db
    except Exception as e:
        print(f"🚨 Database session error: {e}")  # ✅ Catch session errors
    finally:
        db.close()
        print("✅ Database session closed.")  # ✅ Confirm session closes

# Create the tables
def create_db():
    Base.metadata.create_all(bind=engine)

# User model
class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # Add this line to extend the existing table definition

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    height = Column(String)  # Using Float for numerical data
    weight = Column(String)  # Using Float for numerical data
    dob = Column(Date)  # Using Date for date of birth
    gender = Column(String)
    role = Column(String)

    def __init__(self, **kwargs):
        print(f"📌 Initializing User: {kwargs}")  # ✅ Debugging
        super().__init__(**kwargs)

class ExerciseCreate(BaseModel):
    name: str
    description: str
    toughness: str
    media_url: str = None
    tags: List[str] = []
    suggested_reps: int

    class Config:
        from_attributes = True

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    toughness = Column(String, nullable=True)
    media_url = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # Stored as JSON string
    suggested_reps = Column(Integer, nullable=True)

# Fetch user data
def get_user_data(db, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_exercise_by_id(db: Session, exercise_id: int):
    return db.query(Exercise).filter(Exercise.id == exercise_id).first()

def get_exercise_by_tag(db: Session, exercise_tag: str):
    return db.query(Exercise).filter(Exercise.tags == exercise_tag).first()


def get_exercise_by_toughness(db: Session, exercise_toughness: str):
    return db.query(Exercise).filter(Exercise.toughness == exercise_toughness).first()

# Only create tables if this script is run directly
if __name__ == "__main__":
    create_db()
