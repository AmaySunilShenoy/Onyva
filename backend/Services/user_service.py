from Database_Connection.Redis import RedisConnection
import json
import concurrent.futures
import time

redis = RedisConnection.get_redis()

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
    if redis.sismember(f"route:{route_id}", email):
        redis.srem(f"route:{route_id}", email)
        return {"success": "unsubscribed"}

    redis.sadd(f"route:{route_id}", email)
    redis.publish(email, json.dumps({"route_id": route_id, "status": "subscribed"}))
    return {"success": "subscribed"}

def check_membership(route_id, email):
    return redis.sismember(route_id, email)

def get_subscriptions(email: str):
    subscriptions = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(check_membership, route_id, email) for route_id in redis.scan_iter(match="route:*")]
        for future, route_id in zip(concurrent.futures.as_completed(futures), redis.scan_iter(match="route:*")):
            if future.result():
                subscriptions.append(route_id.decode().split(":", 1)[1])
    return subscriptions

def publish_crime_report(email: str, route_id: str, crime_report: str):
    crime_report_list = ['vehicle accident', 'theft', 'assault', 'vandalism']
    if crime_report not in crime_report_list:
        return {"error": "Invalid crime report"}

    report_key = f"route_id:{route_id}:{crime_report}"
    if redis.get(report_key):
        return {"error": "Crime report already published"}

    redis.set(report_key, email) 
    redis.publish(route_id, json.dumps({"route_id": route_id, "crime_report": crime_report}))
    return {"success": "crime report published"}

def fetch_reports_for_route(route_id: str):
    reports = []
    for key in redis.scan_iter(match=f"route_id:{route_id}:*"):
        report = key.decode().split(":")[-1]
        reports.append({"route_id": route_id, "crime_report": report})
    return reports

def get_reports_for_subscriptions(email: str):
    subscriptions = get_subscriptions(email)
    reports = []
    for route_id in subscriptions:
        route_reports = fetch_reports_for_route(route_id)
        reports.extend(route_reports)
    return reports

def get_all_reports():
    reports = []
    for key in redis.scan_iter(match="route_id:*"):
        report = key.decode().split(":")[-1]
        reports.append({"route_id": key.decode().split(":")[1] +":"+ key.decode().split(":")[2], "crime_report": report})
    return reports
