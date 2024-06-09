from Database_Connection.MongoDB import MongoDBConnection
from passlib.context import CryptContext
from fastapi import HTTPException
# getting JWT class
from utils.JWTHandler import JWT

# creating an instance of JWT
jwt = JWT()


# pw hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

mongo = MongoDBConnection()


#create a new user in the database after checking if the email alr exists
def create_user(email: str, password: str):
    try:
        # get the users collection
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

        # creating a jwt token for the user using mongoDB id
        user_document["_id"] = str(result.inserted_id)

        # creating access and refresh tokens
        access_token = jwt.create_access_token(data={"sub": user_document["_id"]})
        refresh_token = jwt.create_refresh_token(data={"sub": user_document["_id"]})

        # returning the tokens
        return {"access_token": access_token, "refresh_token": refresh_token}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    





def get_user(email: str, password: str):
    try:
        # Get the users collection
        users_collection = mongo.get_collection("users")

        # Find the user by email
        stored_user = users_collection.find_one({"email": email})


        # Check if user exists
        if not stored_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify password
        if pwd_context.verify(password, stored_user["hashed_password"]):
            # Convert ObjectId to string
            stored_user["_id"] = str(stored_user["_id"])

            # Create access and refresh tokens
            access_token = jwt.create_access_token(data={"sub": str(stored_user["_id"])})
            refresh_token = jwt.create_refresh_token(data={"sub": str(stored_user["_id"])})

            # Return tokens
            return {"access_token": access_token, "refresh_token": refresh_token}
        
        else:
            # Return error if password is incorrect
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




