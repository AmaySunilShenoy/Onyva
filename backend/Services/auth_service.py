import pymongo
from Database_Connection.MongoDB import MongoDBConnection
from bson import ObjectId
from passlib.context import CryptContext
from fastapi import HTTPException


# pw hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

mongo = MongoDBConnection()
#create a new user in the database after checking if the email alr exists
def create_user(email: str, password: str):
    try:
        users_collection = mongo.get_collection("users")
        # check if the email already exists

        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            raise HTTPException(status_code=400, detail="email already in use")

        # Hash the password
        hashed_password = pwd_context.hash(password)

        # Create user document
        user_document = {
            "email": email,
            "hashed_password": hashed_password
        }

        # Insert user document into the database
        result = users_collection.insert_one(user_document)

        return str(result.inserted_id) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        mongo.close()





# def get_user(user):
#     client = get_mongo_client()
#     users_collection = mongo_db["users"]


#     # Find the user by email
#     stored_user = users_collection.find_one({"email": user.email})
#     if stored_user:
#         # Verify password
#         if pwd_context.verify(user.password, stored_user["hashed_password"]):
#             client.close()
#             return stored_user
#         else:
#             client.close()
#             raise HTTPException(status_code=401, detail="Invalid credentials")
#     else:
#         client.close()
#         raise HTTPException(status_code=404, detail="User not found")