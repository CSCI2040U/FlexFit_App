from sqlalchemy import Column, Integer, String, Date, Enum
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    weight = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    gender = Column(Enum("Male", "Female", "Other", name="genders"), nullable=False)
    role = Column(Enum("admin", "user", name="roles"), default="user", nullable=False)

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    toughness = Column(Enum("Easy", "Medium", "Hard", name="toughness_levels"))
    media_url = Column(String)
    tags = Column(String)  # JSON tags (e.g., "with equipment, outdoor")
    suggested_reps = Column(Integer)
