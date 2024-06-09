from Database_Connection.Redis import RedisConnection
from Database_Connection.MongoDB import MongoDBConnection
from fastapi import HTTPException, Request
from bson import ObjectId
from utils.JWTHandler import JWT

redis = RedisConnection.get_redis()
mongo = MongoDBConnection()


jwt = JWT()
users_collection = mongo.get_collection("users")


# user can update their email
def update_user_email(user_id: str, new_email: str):
    try:
        # Check if the new email is already in use
        existing_email = users_collection.find_one({"email": new_email})
        if existing_email:
            raise HTTPException(status_code=400, detail="The new email is already in use")
        
        # Update the email
        result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"email": new_email}})

        if result.modified_count > 0:
            return {"success": "Email updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

# user can add/ edit in name
def edit_user_name(user_id: str, name: str):
    try:
        # Check if the user exists
        user = users_collection.find({"_id": ObjectId(user_id)})
        if user:
            # Update the name
            result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"name": name}})
            if result.modified_count > 0:
                return {"success": "Name updated successfully"}
            else:
                raise HTTPException(status_code=500, detail="Name not updated")
        else:
            raise HTTPException(status_code=404, detail="User not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# user can delete their name
def delete_user_name(user_id: str):
    try:
        # Check if the user exists
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            # Delete the name
            result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$unset": {"name": ""}})
            if result.modified_count > 0:
                return {"success": "name deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#  user can delete their account
def delete_user(user_id: str):
    try:
        # Check if the user exists
        result = users_collection.delete_one({"_id": ObjectId(user_id)})

        # Check if the user was deleted
        if result.deleted_count > 0:
            return {"success": "User deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def toggle_route_to_fav(route_id: str, request: Request):
    # Get token from request headers bearer token
    token = request.headers.get("Authorization")
    if not token:
        # Hence USEr will have to login to add a route to fav
        raise HTTPException(status_code=401, detail="Token not found")
    try:
        # Get user_id from request state
        user_id = request.state.user_id

        users_collection = mongo.get_collection("users")

        # Check if the user exists
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if the user has a fav_routes field and if not, create it
        if "fav_routes" not in user:
         
            users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"fav_routes": [route_id]}})
            return {"message": "Route added to favorites"}
        else:
            if route_id in user["fav_routes"]:
               
            #    If route_id is present, remove it from the list
                users_collection.update_one({"_id": ObjectId(user_id)}, {"$pull": {"fav_routes": route_id}})
                return {"message": "Route removed from favorites"}
            else:
                # If route_id is not present, add it to the list
                users_collection.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"fav_routes": route_id}})
                return {"message": "Route added to favorites"}

    except Exception as e:
        print("Error:", e)  # Print other exceptions for debugging
        raise HTTPException(status_code=500, detail="Internal server error")