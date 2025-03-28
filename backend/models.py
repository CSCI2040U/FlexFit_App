from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Float, Date, DateTime
from sqlalchemy.orm import relationship

from backend.database import Base  # Import Base from database.py

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    dob = Column(String)
    weight = Column(Integer)
    height = Column(Integer)
    gender = Column(String)
    role = Column(String)

    # ✅ Add this inside the class
    progress_logs = relationship("ProgressLog", back_populates="user", cascade="all, delete-orphan")

class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = {'extend_existing': True}  # Add this line to extend the existing table definition

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    toughness = Column(Enum("Easy", "Medium", "Hard", name="toughness_levels"))
    media_url = Column(String)
    tags = Column(String)  # JSON tags (e.g., "with equipment, outdoor")
    suggested_reps = Column(Integer)


class ProgressLog(Base):
    __tablename__ = "progress_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(DateTime, default=datetime.utcnow)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)

    # ✅ Add this back-reference to the User model
    user = relationship("User", back_populates="progress_logs")

class SavedExercise(Base):
    __tablename__ = "saved_exercises"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)