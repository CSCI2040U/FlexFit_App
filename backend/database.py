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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the tables
def create_db():
    Base.metadata.create_all(bind=engine)

# User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    height = Column(String)  # Using Float for numerical data
    weight = Column(String)  # Using Float for numerical data
    dob = Column(Date)  # Using Date for date of birth

# Fetch user data
def get_user_data(db, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Only create tables if this script is run directly
if __name__ == "__main__":
    create_db()
