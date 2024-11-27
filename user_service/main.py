from fastapi import FastAPI
from user_service.database import get_db_connection
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_db_connection()
    if db is not None:  
        print("Database connected")
        yield
        db.client.close()  # Close the MongoDB connection
        print("Database connection closed")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "User Service is running"}
