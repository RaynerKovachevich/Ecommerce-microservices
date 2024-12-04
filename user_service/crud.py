from .models import Product
from .database import get_db_connection
from bson import ObjectId

def create_product(product: Product):
    db = get_db_connection()
    product_data = product.model_dump()
    result = db["products"].insert_one(product_data)
    product_data["_id"] = str(result.inserted_id)
    return product_data

def get_all_products():
    db = get_db_connection()
    products = db["products"].find()
    return [{**product, "_id":str(product["_id"])} for product in products]

def get_product_by_id(product_id: str):
    db = get_db_connection()
    try:
        product_object_id = ObjectId(product_id)
    except Exception:
        return None
    product = db["products"].find_one({"_id": product_object_id})
    return product

def update_product(product_object_id: ObjectId, product: Product):
    db = get_db_connection()
    try:
        product_object_id = ObjectId(product_object_id)
    except Exception:
        return None
        
    update_product = db["products"].find_one_and_update(
        {"_id": product_object_id},
        {"$set": product.model_dump()},
        return_document=True
    )
    return update_product

def delete_product(product_id: ObjectId):
    db = get_db_connection()
    try:
         product_object_id = ObjectId(product_id)
    except Exception:
        return None

    db["products"].delete_one({"_id": product_object_id})
