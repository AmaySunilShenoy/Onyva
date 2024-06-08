from fastapi import APIRouter, Request
# import func from services
from Database_Connection.Redis import RedisConnection
from Services.path_service import find_path_between_stops, find_closest_stops
import json
router = APIRouter()

redis = RedisConnection.get_redis()

@router.get("/find", tags=["Journey"])
# for loading the data into the Neo4j database
async def find_path(start_latitude: float,start_longitude:float,end_latitude:float, end_longitude:float, time:str,request: Request):
    search_key = f"{start_latitude},{start_longitude},{end_latitude},{end_longitude},{time}"
    if redis.exists(search_key):
        paths = redis.get(search_key)
        return json.loads(paths)

    startStops = find_closest_stops(start_latitude,start_longitude)
    endStops = find_closest_stops(end_latitude,end_longitude)
    all_paths = []
    if startStops is None or endStops is None:
        return {"message": "Failed to find closest stops"}
    for st_stop in startStops:
        start = st_stop['stop_id']
        for en_stop in endStops:
            end = en_stop['stop_id']
            path = find_path_between_stops(start, end,time)
            if path is not None:
                print('path was found between', st_stop['stop_name'],start, 'and', en_stop['stop_name'],end)
                all_paths.append(path)
            else:
                print('path was not found between', st_stop['stop_name'],start, 'and', en_stop['stop_name'],end)

    all_paths.sort(key=lambda x: len(x))

    

    if all_paths is None:
        return {"message": f"Sorry no path was found between ${start} and ${end}"}
    user_id = request.state.user_id
    if user_id is None:
        return {"message": "Session not established. Please provide a user_id in the header."}

    redis.lpush(f"{user_id}-recent_searches", search_key)
    redis.ltrim(f"{user_id}-recent_searches", 0, 4)
    redis.setex(search_key,1800, json.dumps(all_paths))

    return all_paths

@router.get("/find/closest", tags=["Journey"])
async def find_closest(lat: float, lon: float, request: Request):
    search_key = f"{lat},{lon}"
    if redis.exists(search_key):
        station = redis.get(search_key)
        return json.loads(station)
    
    closest_stops = find_closest_stops(lat, lon)
    if closest_stops is None:
        return {"message": "Failed to find closest stops"}
    
    user_id = request.state.user_id
    if user_id is None:
        return {"message": "Session not established. Please provide a user_id in the header."}

    redis.lpush(f"{user_id}-recent_stations", search_key)
    redis.ltrim(f"{user_id}-recent_stations", 0, 4)
    redis.setex(search_key,1800, json.dumps(closest_stops))
    return closest_stops


@router.get("/find/recent", tags=["Journey"])
async def get_recent_searches(request: Request):
    user_id = request.state.user_id
    print(user_id)
    if user_id is None:
        return {"message": "Session not established. Please provide a user_id in the header."}
    recent_searches = redis.lrange(f"{user_id}-recent_searches", 0, 4)
    recent_stations = redis.lrange(f"{user_id}-recent_stations", 0, 4)
    recent_output = []
    for search in recent_searches:
        search_key = search.decode()
        search_result = redis.get(search_key)
        if search_result is None:
            search_result = "The search has expired. Please search again."
        recent_output.append({"search": search_key, "result": search_result})

    for station in recent_stations:
        station_key = station.decode()
        station_result = redis.get(station_key)
        if station_result is None:
            station_result = "The search has expired. Please search again."
        recent_output.append({"search": station_key, "result": station_result})
    return {"recent_searches": [search.decode() for search in recent_searches],"recent_stations": [search.decode() for search in recent_stations] ,"results": recent_output}


# Clear recent searches
@router.get("/clear_recent", tags=["Journey"])
async def clear_recent_searches(request: Request):
    user_id = request.state.user_id
    if user_id is None:
        return {"message": "Session not established. Please provide a user_id in the header."}
    redis.delete(f"{user_id}-recent_searches")
    redis.delete(f"{user_id}-recent_stations")
    return {"message": "Recent searches cleared."}