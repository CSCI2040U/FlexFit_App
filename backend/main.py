import os
import traceback
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, Query, File, UploadFile, Body
import cloudinary
import cloudinary.uploader
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, get_user_data, ExerciseCreate, get_exercise_by_id
from backend.models import Base, Exercise, User, SavedExercise, ProgressLog
from backend.routes import exercises
from backend.schemas import UserCreate, LoginRequest, ExerciseRequest, ExerciseUpdate, ExerciseResponse
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from backend.routes.auth import router as auth_router  # Import the auth router

# FastAPI app initialization
app = FastAPI(
    title="Your API",
    description="API for managing exercises",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Exercise",
            "description": "Operations related to exercises",
        }
    ]
)

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
)


# Secret key for encoding and decoding JWT tokens
SECRET_KEY = "your_secret_key"  # Change this to a secure random key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Set token expiration time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Function to create a JWT token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Function to verify the token
def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token or expired")


# Include routes for authentication

app.include_router(auth_router, prefix="/auth")
app.include_router(exercises.router, prefix="/api", tags=["Workouts"])


Base.metadata.create_all(bind=engine)  # Creates tables if they don't exist


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/add_exercise/")
def add_exercise(exercise: ExerciseRequest, db: Session = Depends(get_db)):
    print("🔥 ADD_EXERCISE route loaded")
    print("📦 Exercise payload:", exercise)

    default_image_url = "https://res.cloudinary.com/dudftatqj/image/upload/v1741316241/logo_iehkuj.png"
    media_url = exercise.media_url or default_image_url

    new_exercise = Exercise(
        name=exercise.name,
        description=exercise.description,
        toughness=exercise.toughness,
        media_url=media_url,
        tags=json.dumps(exercise.tags),
        suggested_reps=exercise.suggested_reps
    )

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    return {"message": "Exercise added successfully", "exercise_id": new_exercise.id}


# Login route to authenticate users and return a JWT token
@app.post("/login/")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not check_password_hash(user.password_hash, request.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create JWT token for the authenticated user
    access_token = create_access_token(data={"sub": user.email})

    user_data = get_user_data(db, user.id)

    return {"access_token": access_token,
            "token_type": "bearer",
            "user": user_data}

@app.post("/signup/")
def signup(user_info: UserCreate, db: Session = Depends(get_db)):
    """Handles user registration and adds a new user to the database."""
    try:
        print(f"📌 Received Sign-Up Data: {user_info}")  # Debugging

        # Check if the email is already registered
        existing_user = db.query(User).filter(User.email == user_info.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the password
        hashed_password = generate_password_hash(user_info.password, method='pbkdf2:sha256')

        # ✅ Convert dob from string to date (Already handled in Pydantic model)
        parsed_dob = user_info.dob


        # ✅ Create new user
        new_user = User(
            username=user_info.username,
            full_name=user_info.full_name,
            email=user_info.email,
            password_hash=hashed_password,
            dob=parsed_dob,
            gender=user_info.gender,
            height=user_info.height,
            weight=user_info.weight,
            role=user_info.role
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print(f"✅ Successfully Created User: {new_user.email}")
        return {"message": "User created successfully", "user_id": new_user.id}

    except Exception as e:
        print(f"🚨 ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/toggle_saved/{user_id}/{exercise_id}")
def toggle_saved_exercise(user_id: int, exercise_id: int, db: Session = Depends(get_db)):
    existing = db.query(SavedExercise).filter_by(user_id=user_id, exercise_id=exercise_id).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"status": "removed"}
    else:
        new_entry = SavedExercise(user_id=user_id, exercise_id=exercise_id)
        db.add(new_entry)
        db.commit()
        return {"status": "saved"}


@app.get("/saved_exercises/{user_id}")
def get_saved_exercises(user_id: int, db: Session = Depends(get_db)):
    saved = db.query(SavedExercise.exercise_id).filter_by(user_id=user_id).all()
    return [item.exercise_id for item in saved]


# Protected route that requires JWT token
@app.get("/protected/")
def protected_route(token: str = Depends(oauth2_scheme)):
    # Verify the token
    user = verify_access_token(token)
    return {"message": "You have access", "user": user}


# Route to fetch user information (example)
@app.get("/user/{user_id}")
def get_user_info(user_id: int, db: Session = Depends(get_db)):
    user_data = get_user_data(db, user_id)
    if user_data:
        height, weight, username = user_data
        return {"height": height, "weight": weight, "username": username}
    return {"error": "User not found"}


@app.post("/logout/")
def logout():
    """Invalidate the token on the client side."""
    return {"message": "Logged out successfully"}


# Route to get exercises (example)
@app.get("/exercises/")
def get_exercises(
        search_query: str = Query(None),
        db: Session = Depends(get_db)
):
    """Fetches all exercises and converts JSON tags back to Python lists."""
    exercises = db.query(Exercise).all()
    exercises_query = db.query(Exercise)

    if search_query:  # ✅ Apply search filter ONLY if search_query exists
        search_query = f"%{search_query.lower()}%"  # ✅ SQL wildcard search
        exercises_query = exercises_query.filter(Exercise.name.ilike(search_query))

    exercises = exercises_query.all()

    # Convert JSON string back to list
    exercises_list = []
    for ex in exercises:
        exercises_list.append({
            "id": ex.id,
            "name": ex.name,
            "description": ex.description,
            "toughness": ex.toughness,
            "media_url": ex.media_url,
            "tags": json.loads(ex.tags) if ex.tags else [],  # ✅ Convert back to list
            "suggested_reps": ex.suggested_reps
        })

    return exercises_list if exercises_list else {"error": "No exercises found"}

@app.get("/exercise/{exercise_id}")
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    try:
        exercise = get_exercise_by_id(db, exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")


        try:
            tags_list = json.loads(exercise.tags) if exercise.tags else []
        except json.decoder.JSONDecodeError:
            tags_list = []

        return {
            "name": exercise.name,
            "image_url": exercise.media_url,
            "description": exercise.description,
            "tags": tags_list,
            "suggested_reps": exercise.suggested_reps,
            "toughness": exercise.toughness
        }
    except Exception as e:
        print(f"❌ Internal Server Error: {e}")
        print(traceback.format_exc())  # ✅ This will show the full error in logs
        raise HTTPException(status_code=500, detail="Internal Server Error")

from backend.schemas import ExerciseUpdate, ExerciseResponse  # ✅ Import schema

@app.put("/edit_exercise/{exercise_id}", response_model=ExerciseResponse)
def edit_exercise(exercise_id: int, workout_data: ExerciseUpdate, db: Session = Depends(get_db)):
    workout = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    updates = workout_data.dict(exclude_unset=True)

    if "tags" in updates and isinstance(updates["tags"], list):
        updates["tags"] = json.dumps(updates["tags"])

    for attr, value in updates.items():
        setattr(workout, attr, value)

    db.commit()
    db.refresh(workout)

    return ExerciseResponse(
        id=workout.id,
        name=workout.name,
        description=workout.description,
        toughness=workout.toughness,
        tags=json.loads(workout.tags) if workout.tags else [],
        media_url=workout.media_url,
        suggested_reps=workout.suggested_reps
    )



@app.put("/user/{user_id}/update")
def update_user_info(user_id: int, data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "height" in data:
        user.height = data["height"]
    if "weight" in data:
        user.weight = data["weight"]

    db.commit()
    db.refresh(user)
    return {"message": "User info updated successfully"}

@app.post("/progress/{user_id}")
def log_progress(user_id: int, height: float = None, weight: float = None, db: Session = Depends(get_db)):
    entry = ProgressLog(user_id=user_id, height=height, weight=weight)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"message": "Progress logged successfully"}

@app.get("/progress/{user_id}")
def get_progress(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(ProgressLog).filter(ProgressLog.user_id == user_id).order_by(ProgressLog.date).all()
    return [
        {
            "date": log.date,
            "height": log.height,
            "weight": log.weight
        }
        for log in logs
    ]

@app.post("/upload_workout_image/")
async def upload_workout_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        result = cloudinary.uploader.upload(contents, folder="workouts/")
        return {"url": result["secure_url"]}
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")
