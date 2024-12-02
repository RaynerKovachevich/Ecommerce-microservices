from fastapi import FastAPI, HTTPException, Depends
from pymongo.errors import DuplicateKeyError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from user_service.database import get_db_connection


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


app = FastAPI()


def get_db():
    db = get_db_connection()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    return db

@app.get("/")
def root():
    return {"message": "User Service is running"}


@app.post("/users/register")
def register_user(user: UserCreate, db=Depends(get_db)):
    users_collection = db["users"]
    hashed_password = pwd_context.hash(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password
    }

    try:
        users_collection.insert_one(user_data)
        return {"message": "User registered successfully"}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email or username already exists")
    
@app.get("/users/{user_id}")
def get_user_by_id(user_id: str, db=Depends(get_db)):
    users_collection = db["users"]

    try:
        user_object_id = ObjectId(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = users_collection.find_one({"_id": user_object_id})

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"]
    }    
