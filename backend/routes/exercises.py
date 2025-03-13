from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Exercise

router = APIRouter(
    prefix="/exercises",  # ✅ Ensures the correct endpoint
    tags=["Exercises"]
)


@router.delete("/{exercise_id}", response_model=dict)
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    db.delete(exercise)
    db.commit()

    return {"message": "Exercise deleted successfully"}
