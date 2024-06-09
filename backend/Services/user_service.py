from Database_Connection.Redis import RedisConnection
from Database_Connection.MongoDB import MongoDBConnection
import json
import concurrent.futures
from fastapi import HTTPException
from bson import ObjectId

redis = RedisConnection.get_redis()
mongo = MongoDBConnection()

# Background task to handle messages
def handle_messages(email: str, websocket):
    pubsub = redis.pubsub()
    pubsub.subscribe(email)
    try:
        for message in pubsub.listen():
            if message['type'] == 'message' and message['channel'].decode() == email:
                data = message['data'].decode()
                print(f"Sending message to {email}: {data}")
                websocket.send_text(data)
    except Exception as e:
        print(f"Error handling messages for {email}: {e}")

def subscribe_to_route(route_id: str, email: str):
    # Check if already subscribed
    if redis.sismember(f"route:{route_id}", email):
        redis.srem(f"route:{route_id}", email)
        return {"success": "unsubscribed"}

    # Subscribe and add to the route set
    redis.sadd(f"route:{route_id}", email)
    redis.publish(email, json.dumps({"route_id": route_id, "status": "subscribed"}))
    return {"success": "subscribed"}


def check_membership(route_id, email):
    return redis.sismember(route_id, email)

#  Parellezation of the check_membership function'
def get_subscriptions(email: str):
    subscriptions = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(check_membership, route_id, email) for route_id in redis.scan_iter(match="route:*")]
        for future, route_id in zip(concurrent.futures.as_completed(futures), redis.scan_iter(match="route:*")):
            if future.result():
                subscriptions.append(route_id.decode().split(":", 1)[1])

    return subscriptions

# user can report a crime and it will be published to all subscribers
def publish_crime_report(email: str,route_id, crime_report: str):
    crime_report_list = ['vehicle accident', 'theft', 'assault', 'vandalism']
    if crime_report not in crime_report_list:
        return {"error": "Invalid crime report"}
    # can be published only once in 1 hour Hence check if already published
    if redis.get(f"route_id:{route_id}:{crime_report}"):
        return {"error": "Crime report already published"}
    # Publish the crime report to all subscribers
    redis.publish(email, json.dumps({"route_id": route_id, "crime_report": crime_report}))
    return {"success": "crime report published"}


# user can update their email
def update_user_email(user_id: str, new_email: str):
    try:
        users_collection = mongo.get_collection("users")
        existing_email = users_collection.find_one({"email": new_email})
        if existing_email:
            raise HTTPException(status_code=400, detail="The new email is already in use")
        filtered_data = {"_id": ObjectId(user_id)}
        updated_data = {"$set": {"email": new_email}}
        result = users_collection.update_one(filtered_data, updated_data)
        if result.matched_count > 0:
            return {"success": "Email updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

# user can add/ edit in name
def edit_user_name(user_id: str, name: str):
    try:
        users_collection = mongo.get_collection("users")
        filtered_data = users_collection.find_one({"_id": ObjectId(user_id)})
        if filtered_data:
            users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"name": name}})
            return {"success": "Name added successfully"}

        else:
            raise HTTPException(status_code=404, detail="User not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# user can delete their name
def delete_user_name(user_id: str):
    try:
        users_collection = mongo.get_collection("users")
        result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$unset": {"name": ""}})
        if result.modified_count > 0:
            return {"success": "name deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))