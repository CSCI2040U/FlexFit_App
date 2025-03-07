from sqlalchemy import Column, Integer, String, Enum
from backend.database import Base  # Import Base from database.py

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # Add this line to extend the existing table definition

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    dob = Column(String)  # You can change this to Date if you want
    weight = Column(Integer)
    height = Column(Integer)
    gender = Column(String)
    role = Column(String)

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
