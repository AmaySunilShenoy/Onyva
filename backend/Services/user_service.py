# using MONGODB for CRUD operations for users 
from Database_Connection.MongoDB import MongoDBConnection
from bson import ObjectId
from fastapi import HTTPException

mongo = MongoDBConnection()

# CRUD operations for users

def add_route_to_fav(user_id: str, route_id: str):
    try:
        users_collection = mongo.get_collection("users")
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if route_id in user["fav_routes"]:
            # unfavourite the route
            user["fav_routes"].remove(route_id)
            status = "unfavourited"
        else:
            user["fav_routes"].append(route_id)
            status = "favourited"
        # update the user document
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": user})
        return {"status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))