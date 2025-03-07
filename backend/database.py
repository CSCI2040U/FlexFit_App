from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "mysql+mysqlconnector://root:SwastikEngSolution@127.0.0.1:3306/flexfit_app"

# This is the Base class that all your models will inherit from
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

# Call this function to create the tables when the application starts
create_db()
