from .models import Product
from .database import get_db_connection

def create_product(product: Product):
    db = get_db_connection()
    product_data = product.model_dump()
    db["products"].insert_one(product_data)
    return product_data

def get_all_products():
    db = get_db_connection()
    products = db["products"].find()
    return list(products)

def get_product_by_id(product_id: str):
    db = get_db_connection()
    product = db["products"].find_one({"_id": product_id})
    return product

def update_product(product_id: str, product: Product):
    db = get_db_connection()
    update_product = db["products"].find_one_and_update(
        {"_id": product_id},
        {"$set": product.model_dump()},
        return_document=True
    )
    return update_product

def delete_product(product_id: str):
    db = get_db_connection()
    db["products"].delete_one({"_id": product_id})
