from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, get_user_data, ExerciseCreate
from backend.models import Base, Exercise, User
from backend.schemas import UserCreate, LoginRequest
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

# FastAPI app initialization
app = FastAPI()

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
from backend.routes.auth import router as auth_router  # Import the auth router

app.include_router(auth_router, prefix="/auth")

Base.metadata.create_all(bind=engine)  # Creates tables if they don't exist


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/add_exercise/")
def add_exercise(exercise: dict, db: Session = Depends(get_db)):
    """Adds a new exercise to the database with debugging logs."""
    try:
        print(f"📌 Received Exercise Data: {exercise}")  # ✅ Log received data

        # Ensure required fields exist
        required_fields = ["name", "description", "toughness", "tags"]
        for field in required_fields:
            if field not in exercise:
                raise HTTPException(status_code=400, detail=f"{field} is required")

        if isinstance(exercise.get("tags"), list):
            tags_json = json.dumps(exercise["tags"])  # Convert to string
        elif isinstance(exercise.get("tags"), str):
            tags_json = exercise["tags"]  # Already a valid JSON string
        else:
            tags_json = "[]"  # Default to empty list if invalid

        # Set default image URL if media_url is not provided
        default_image_url = "https://res.cloudinary.com/dudftatqj/image/upload/v1741316241/logo_iehkuj.png"
        media_url = exercise.get("media_url", default_image_url)  # ✅ Assign default if missing

        # ✅ Create new exercise
        new_exercise = Exercise(
            name=exercise["name"],
            description=exercise["description"],
            toughness=exercise["toughness"],
            media_url=media_url,
            tags=tags_json,
            suggested_reps=exercise.get("suggested_reps", 10)  # Default to 10 reps
        )

        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)

        print(f"✅ Successfully Added Exercise: {new_exercise}")  # ✅ Debug Success
        return {"message": "Exercise added successfully", "exercise_id": new_exercise.id, "media_url": media_url}

    except Exception as e:
        print(f"🚨 ERROR: {e}")  # ✅ Debugging
        raise HTTPException(status_code=500, detail=str(e))  # Return actual error


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
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup/")
def signup(user_info: dict, db: Session = Depends(get_db)):
    # Ensure that all necessary fields are provided
    required_fields = ["username", "email", "password", "role", "full_name", "dob", "gender", "height", "weight"]
    for field in required_fields:
        if field not in user_info:
            raise HTTPException(status_code=400, detail=f"{field} is required")

    # Check if the user already exists
    existing_user = db.query(User).filter(User.email == user_info['email']).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before saving it
    hashed_password = generate_password_hash(user_info['password'], method='pbkdf2:sha256')

    # Create a new user object with all the fields
    new_user = User(
        username=user_info['username'],
        full_name=user_info['full_name'],
        email=user_info['email'],
        password_hash=hashed_password,
        dob=user_info['dob'],
        gender=user_info['gender'],
        height=user_info['height'],
        weight=user_info['weight'],
        role=user_info['role']
    )

    # Save the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id}

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
        height, weight = user_data
        return {"height": height, "weight": weight}
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
