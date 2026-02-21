from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection (local)
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["smartphone_sales"]

# Collections
smartphones_collection = db["smartphones"]
sales_collection = db["sales_data"]
predictions_collection = db["predictions"]
feature_importance_collection = db["feature_importance"]

def init_database():
    # Create indexes
    smartphones_collection.create_index("model", unique=True)
    sales_collection.create_index([("model", 1), ("month", 1)], unique=True)
    
    # Load sample data if collections are empty
    if smartphones_collection.count_documents({}) == 0:
        load_sample_data()

def load_sample_data():
    # Extended sample smartphones with more brands
    sample_phones = [
        # Apple
        {"brand": "Apple", "model": "iPhone 13", "price": 799, "ram": 4, "storage": 128, "battery": 3240, "camera_mp": 12, "os": "iOS", "launch_date": "2021-09-24"},
        {"brand": "Apple", "model": "iPhone 14", "price": 899, "ram": 6, "storage": 128, "battery": 3279, "camera_mp": 12, "os": "iOS", "launch_date": "2022-09-16"},
        {"brand": "Apple", "model": "iPhone 15", "price": 999, "ram": 6, "storage": 128, "battery": 3349, "camera_mp": 48, "os": "iOS", "launch_date": "2023-09-22"},
        
        # Samsung
        {"brand": "Samsung", "model": "Galaxy S21", "price": 799, "ram": 8, "storage": 128, "battery": 4000, "camera_mp": 64, "os": "Android", "launch_date": "2021-01-29"},
        {"brand": "Samsung", "model": "Galaxy S22", "price": 899, "ram": 8, "storage": 128, "battery": 3700, "camera_mp": 50, "os": "Android", "launch_date": "2022-02-25"},
        {"brand": "Samsung", "model": "Galaxy S23", "price": 999, "ram": 8, "storage": 128, "battery": 3900, "camera_mp": 50, "os": "Android", "launch_date": "2023-02-17"},
        
        # Google
        {"brand": "Google", "model": "Pixel 6", "price": 599, "ram": 8, "storage": 128, "battery": 4614, "camera_mp": 50, "os": "Android", "launch_date": "2021-10-28"},
        {"brand": "Google", "model": "Pixel 7", "price": 699, "ram": 8, "storage": 128, "battery": 4355, "camera_mp": 50, "os": "Android", "launch_date": "2022-10-13"},
        {"brand": "Google", "model": "Pixel 8", "price": 799, "ram": 8, "storage": 128, "battery": 4575, "camera_mp": 50, "os": "Android", "launch_date": "2023-10-12"},
        
        # OnePlus
        {"brand": "OnePlus", "model": "9 Pro", "price": 969, "ram": 12, "storage": 256, "battery": 4500, "camera_mp": 48, "os": "Android", "launch_date": "2021-03-23"},
        {"brand": "OnePlus", "model": "10 Pro", "price": 899, "ram": 12, "storage": 256, "battery": 5000, "camera_mp": 48, "os": "Android", "launch_date": "2022-01-11"},
        {"brand": "OnePlus", "model": "11", "price": 799, "ram": 16, "storage": 256, "battery": 5000, "camera_mp": 50, "os": "Android", "launch_date": "2023-02-07"},
        
        # Xiaomi
        {"brand": "Xiaomi", "model": "Mi 11", "price": 749, "ram": 8, "storage": 128, "battery": 4600, "camera_mp": 108, "os": "Android", "launch_date": "2021-01-01"},
        {"brand": "Xiaomi", "model": "12 Pro", "price": 899, "ram": 12, "storage": 256, "battery": 4600, "camera_mp": 50, "os": "Android", "launch_date": "2022-03-15"},
        {"brand": "Xiaomi", "model": "13 Pro", "price": 999, "ram": 12, "storage": 256, "battery": 4820, "camera_mp": 50, "os": "Android", "launch_date": "2023-02-26"},
        
        # Oppo
        {"brand": "Oppo", "model": "Find X5 Pro", "price": 1099, "ram": 12, "storage": 256, "battery": 5000, "camera_mp": 50, "os": "Android", "launch_date": "2022-02-24"},
        {"brand": "Oppo", "model": "Reno 8 Pro", "price": 599, "ram": 12, "storage": 256, "battery": 4500, "camera_mp": 50, "os": "Android", "launch_date": "2022-07-11"},
        {"brand": "Oppo", "model": "Find N2", "price": 1199, "ram": 16, "storage": 512, "battery": 4520, "camera_mp": 50, "os": "Android", "launch_date": "2022-12-15"},
        
        # Vivo
        {"brand": "Vivo", "model": "X90 Pro", "price": 999, "ram": 12, "storage": 256, "battery": 4870, "camera_mp": 50, "os": "Android", "launch_date": "2022-11-22"},
        {"brand": "Vivo", "model": "V27 Pro", "price": 449, "ram": 8, "storage": 128, "battery": 4600, "camera_mp": 50, "os": "Android", "launch_date": "2023-03-01"},
        {"brand": "Vivo", "model": "X Fold", "price": 1299, "ram": 12, "storage": 256, "battery": 4600, "camera_mp": 50, "os": "Android", "launch_date": "2022-04-11"},
        
        # Redmi
        {"brand": "Redmi", "model": "Note 11 Pro", "price": 299, "ram": 6, "storage": 128, "battery": 5000, "camera_mp": 108, "os": "Android", "launch_date": "2022-02-09"},
        {"brand": "Redmi", "model": "K50 Pro", "price": 499, "ram": 12, "storage": 256, "battery": 5000, "camera_mp": 108, "os": "Android", "launch_date": "2022-03-17"},
        {"brand": "Redmi", "model": "Note 12 Pro", "price": 329, "ram": 8, "storage": 128, "battery": 5000, "camera_mp": 50, "os": "Android", "launch_date": "2022-10-27"},
        
        # Nothing
        {"brand": "Nothing", "model": "Phone 1", "price": 399, "ram": 8, "storage": 128, "battery": 4500, "camera_mp": 50, "os": "Android", "launch_date": "2022-07-12"},
        {"brand": "Nothing", "model": "Phone 2", "price": 499, "ram": 12, "storage": 256, "battery": 4700, "camera_mp": 50, "os": "Android", "launch_date": "2023-07-11"},
        
        # Realme
        {"brand": "Realme", "model": "GT 2 Pro", "price": 599, "ram": 12, "storage": 256, "battery": 5000, "camera_mp": 50, "os": "Android", "launch_date": "2022-01-04"},
        {"brand": "Realme", "model": "GT Neo 3", "price": 449, "ram": 8, "storage": 128, "battery": 5000, "camera_mp": 50, "os": "Android", "launch_date": "2022-03-22"},
        {"brand": "Realme", "model": "11 Pro", "price": 329, "ram": 8, "storage": 128, "battery": 5000, "camera_mp": 108, "os": "Android", "launch_date": "2023-05-15"},
        
        # Lenovo
        {"brand": "Lenovo", "model": "Legion Phone Duel 2", "price": 799, "ram": 16, "storage": 256, "battery": 5500, "camera_mp": 64, "os": "Android", "launch_date": "2021-04-08"},
        {"brand": "Lenovo", "model": "K12 Pro", "price": 199, "ram": 4, "storage": 64, "battery": 5000, "camera_mp": 64, "os": "Android", "launch_date": "2020-12-09"},
        
        # Motorola
        {"brand": "Motorola", "model": "Edge 30 Pro", "price": 699, "ram": 12, "storage": 256, "battery": 4800, "camera_mp": 50, "os": "Android", "launch_date": "2022-02-24"},
        {"brand": "Motorola", "model": "Razr 2022", "price": 899, "ram": 8, "storage": 256, "battery": 3500, "camera_mp": 50, "os": "Android", "launch_date": "2022-08-11"},
        
        # Sony
        {"brand": "Sony", "model": "Xperia 1 IV", "price": 1299, "ram": 12, "storage": 256, "battery": 5000, "camera_mp": 12, "os": "Android", "launch_date": "2022-06-11"},
        {"brand": "Sony", "model": "Xperia 5 IV", "price": 899, "ram": 8, "storage": 128, "battery": 5000, "camera_mp": 12, "os": "Android", "launch_date": "2022-09-22"},
        
        # Asus
        {"brand": "Asus", "model": "ROG Phone 6", "price": 999, "ram": 16, "storage": 512, "battery": 6000, "camera_mp": 50, "os": "Android", "launch_date": "2022-07-05"},
        {"brand": "Asus", "model": "Zenfone 9", "price": 699, "ram": 8, "storage": 128, "battery": 4300, "camera_mp": 50, "os": "Android", "launch_date": "2022-07-28"},
        
        # Nokia
        {"brand": "Nokia", "model": "G60 5G", "price": 299, "ram": 4, "storage": 64, "battery": 4500, "camera_mp": 50, "os": "Android", "launch_date": "2022-09-01"},
        {"brand": "Nokia", "model": "X30 5G", "price": 399, "ram": 6, "storage": 128, "battery": 4200, "camera_mp": 50, "os": "Android", "launch_date": "2022-09-01"},
    ]
    smartphones_collection.insert_many(sample_phones)