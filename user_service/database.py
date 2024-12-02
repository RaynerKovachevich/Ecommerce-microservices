import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError  

def get_db_connection():
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)  
        db_name = os.getenv("MONGO_DB_NAME", "ecommerce_db")
        db = client[db_name]
        
        client.server_info()
        print("Connected to MongoDB successfully")

        if "users" not in db.list_collection_names():
            db.create_collection("users")
        db["users"].create_index("email", unique=True)
        db["users"].create_index("username", unique=True)    
            
        return db
    except ServerSelectionTimeoutError as e:
        print("Failed to connect to MongoDB:", e)
        return None
