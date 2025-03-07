from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, get_user_data
from backend.models import Base, Exercise, User
from backend.schemas import UserCreate, LoginRequest
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi import FastAPI
from backend.routes.auth import router as auth_router  # Import the auth router

app = FastAPI()

# Include the auth router with the prefix /auth
app.include_router(auth_router, prefix="/auth")


Base.metadata.create_all(bind=engine)  # Creates tables if they don't exist

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/user/{user_id}")
def get_user_info(user_id: int, db: Session = Depends(get_db)):
    user_data = get_user_data(db, user_id)
    if user_data:
        height, weight = user_data
        return {"height": height, "weight": weight}
    return {"error": "User not found"}

@app.post("/login/")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not check_password_hash(user.password_hash, request.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.id}


# Signup route (for registering users)
@app.post("/signup/")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before saving it
    hashed_password = generate_password_hash(user.password, method='pbkdf2:sha256')

    # Create a new user object
    new_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_password,
        dob=user.dob,
        weight=user.weight,
        height=user.height,
        gender=user.gender,
        role=user.role
    )

    # Save the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id}
