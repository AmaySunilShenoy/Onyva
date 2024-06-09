from Database_Connection.Redis import RedisConnection
import json
import concurrent.futures
from fastapi import WebSocket

redis = RedisConnection.get_redis()

# Websocket function to handle pubsub messages
async def handle_messages(user_id: str, websocket: WebSocket):

    # Subscribe to the user's channel (this will be used to forward message to the user depending on which routes they are subscribed to)
    pubsub = redis.pubsub()
    pubsub.subscribe(user_id)

    # Listen for messages on the user's channel
    try:
        for message in pubsub.listen():
            if message['type'] == 'message' and message['channel'].decode() == user_id:
                data = message['data'].decode()
                print(f"Sending message to {user_id}: {data}")
                await websocket.send_text(data)
    except Exception as e:
        print(f"Error handling messages for {user_id}: {e}")


# Subscribe to route for the given user
def toggle_subscribtion_to_route(route_id: str, user_id: str):

    # If the user is already subscribed, unsubscribe
    if redis.sismember(f"route:{route_id}", user_id):
        redis.srem(f"route:{route_id}", user_id)
        return {"success": "unsubscribed"}

    # If the user is not subscribed, subscribe
    redis.sadd(f"route:{route_id}", user_id)
    return {"success": "subscribed"}

# Check if the user is subscribed to the given route
def check_membership(route_id, user_id):
    return redis.sismember(route_id, user_id)


# Get all the subscriptions for a user
def get_subscriptions(user_id: str):
    # init empty list
    subscriptions = []

    # Use ThreadPoolExecutor to check membership for all routes in parallel (for faster execution)
    with concurrent.futures.ThreadPoolExecutor() as executor:

        # Submit a task for each route
        futures = [executor.submit(check_membership, route_id, user_id) for route_id in redis.scan_iter(match="route:*")]

        # Wait for all tasks to complete
        for future, route_id in zip(concurrent.futures.as_completed(futures), redis.scan_iter(match="route:*")):
            if future.result():
                subscriptions.append(route_id.decode().split(":", 1)[1])

    # return the list of subscriptions
    return subscriptions

# Function to publish a report for a given route
def publish_crime_report(user_id, route_id, crime_report):

    # List of valid crime report types
    crime_report_list = ['accident', 'theft', 'assault', 'vandlism', 'lost bag', 'delay', 'other'] 

    # Check if the crime report is valid
    if crime_report not in crime_report_list:
        return {"error": "Invalid crime report type. Please choose from: accident, theft, assault, vandalism, lost bag, delay, other"}


    # Check if the same report has already been published for the given route
    report_key = f"route_id:{route_id}:{crime_report}"
    if redis.get(report_key):
        return {"error": "Crime report already published"}

    # Store the report in redis and publish it to all subscribers
    redis.set(report_key, user_id) 
    redis.publish(route_id, json.dumps({"route_id": route_id, "crime_report": crime_report}))

    return {"success": "crime report published"}


# Get all the crime reports for a given route
def fetch_reports_for_route(route_id: str):
    # init empty list
    reports = []

    # Loop through all keys in redis and get the reports for the given route
    for key in redis.scan_iter(match=f"route_id:{route_id}:*"):
        report = key.decode().split(":")[-1]
        reports.append({"route_id": route_id, "crime_report": report})

    # return the list of reports
    return reports

# Get all the crime reports for a given route
def get_reports_for_route(route_id: str):
    reports = []

    # Loop through all keys in redis and get the reports for the given route
    for key in redis.scan_iter(match=f"route_id:{route_id}:*"):
        report = key.decode().split(":")[-1]
        reports.append({"route_id": route_id, "crime_report": report})

    return reports


# Get all the crime reports for the routes the user is subscribed to
def get_reports_for_all_subscriptions(user_id: str):
    # Get all the subscriptions for the user
    subscriptions = get_subscriptions(user_id)
    reports = []

    # Loop through all subscriptions and get the reports for each route
    for route_id in subscriptions:
        route_reports = fetch_reports_for_route(route_id)
        reports.extend(route_reports)
    return reports


# Get all the crime reports for all routes
def get_all_reports():
    reports = []

    # Loop through all keys in redis and get the reports for all routes
    for key in redis.scan_iter(match="route_id:*"):
        report = key.decode().split(":")[-1]
        reports.append({"route_id": key.decode().split(":")[1] +":"+ key.decode().split(":")[2], "crime_report": report})
    
    # return the list of reports
    return reports
