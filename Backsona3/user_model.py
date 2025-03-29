from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client.HydrAI
users_collection = db.Users

def create_user(username: str, password: str):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {
        "username": username,
        "password": hashed_password.decode('utf-8')
    }
    result = users_collection.insert_one(user)
    return result.inserted_id

def verify_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if not user:
        return False
    
    stored_password = user["password"].encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), stored_password)

def user_exists(username: str):
    return users_collection.find_one({"username": username}) is not None