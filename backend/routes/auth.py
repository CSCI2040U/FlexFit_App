from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import get_db  # Importing the get_db function
from backend.schemas import LoginRequest  # Assuming you have this schema defined
from backend.models import User
from werkzeug.security import check_password_hash

router = APIRouter()

# Login route
@router.post("/login/")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Query the user from the database based on email
    user = db.query(User).filter(User.email == request.email).first()

    # If the user is not found, raise an exception
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the password matches the stored hashed password
    if not check_password_hash(user.password_hash, request.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # If successful, return a message and user id
    return {"message": "Login successful", "user_id": user.id}
