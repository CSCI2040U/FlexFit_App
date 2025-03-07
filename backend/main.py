from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend.models import Base, Exercise
from typing import List

app = FastAPI()

Base.metadata.create_all(bind=engine)  # Creates tables if they don't exist

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/exercises/")
def get_exercises(db: Session = Depends(get_db)):
    exercises = db.query(Exercise).all()
    return [{"id": e.id, "name": e.name, "description": e.description,
             "toughness": e.toughness, "media_url": e.media_url,  # ✅ Ensure this is included
             "tags": e.tags, "suggested_reps": e.suggested_reps} for e in exercises]
