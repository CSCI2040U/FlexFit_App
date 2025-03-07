from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, get_user_data
from backend.models import Base, Exercise, User
from backend.schemas import UserCreate, LoginRequest
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
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


# Route to get exercises (example)
@app.get("/exercises/")
def get_exercises(db: Session = Depends(get_db)):
    exercises = db.query(Exercise).all()  # Fetch exercises from the database
    if exercises:
        return exercises
    raise HTTPException(status_code=404, detail="No exercises found")
