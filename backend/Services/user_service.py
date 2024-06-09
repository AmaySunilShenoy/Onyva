# using MONGODB for CRUD operations for users 
from Database_Connection.MongoDB import MongoDBConnection
from bson import ObjectId
from fastapi import HTTPException, Request
from Services.JWTHandler import JWT


mongo = MongoDBConnection()

# CRUD operations for users
jwt = JWT()

def toggle_route_to_fav(route_id: str, request: Request):
    # Get token from request headers bearer token
    token = request.headers.get("Authorization")
    if not token:
        # HENCE USEr will have to login to add a route to fav
        raise HTTPException(status_code=401, detail="Token not found")
    try:
        user_id = request.state.user_id
        users_collection = mongo.get_collection("users")
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if "fav_routes" not in user:
         
            users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"fav_routes": [route_id]}})
            return {"message": "Route added to favorites"}
        else:
            if route_id in user["fav_routes"]:
               
                users_collection.update_one({"_id": ObjectId(user_id)}, {"$pull": {"fav_routes": route_id}})
                return {"message": "Route removed from favorites"}
            else:
                # If route_id is not present, add it to the list
                users_collection.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"fav_routes": route_id}})
                return {"message": "Route added to favorites"}

    except Exception as e:
        print("Error:", e)  # Print other exceptions for debugging
        raise HTTPException(status_code=500, detail="Internal server error")
