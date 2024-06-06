from Database_Connection.Redis import RedisConnection
import json
import concurrent.futures

redis = RedisConnection.get_redis()

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


