from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from .models import Product
from .crud import create_product, get_all_products, get_product_by_id, update_product, delete_product
from pymongo.errors import DuplicateKeyError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from user_service.database import get_db_connection
import jwt
from datetime import datetime, timedelta, timezone

JWT_SECRET = "Ray21097019"
JWT_ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")



class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


def get_db():
    db = get_db_connection()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    return db

def generate_jwt(user_data):
    expiration = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {
        "user_id": str(user_data["_id"]),
        "exp": expiration
    }
    
    token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return token

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


@app.post("/users/login")
def login_user(user: UserCreate, db=Depends(get_db)):
    users_collection = db["users"]
    user_data = users_collection.find_one({"email": user.email})
    if not user_data or not pwd_context.verify(user.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = generate_jwt(user_data)
    return {"token": token}
    


@app.post("/products/")
def created_product_endpoint(product: Product):
    created_product = create_product(product)
    return {"message": "Product created successfully", "product": created_product}

@app.get("/products/")
def get_products_endpoint():
    products = get_all_products()
    return {"products": products}

@app.get("/products/{product_id}")
def get_product_by_id_endpoint(product_id: str):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product":product}

@app.put("/products/{product_id}")
def update_product_endpoint(product_id: str, product: Product):
    update_product = update_product(product_id, product)
    if not update_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product update succesfully", "product": update_product}

@app.delete("/products/{product_id}")
def delete_product_endpoint(product_id: str):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    delete_product(product_id)
    return {"message": "Product deleted succesfully"}