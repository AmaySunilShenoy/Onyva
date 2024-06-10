from fastapi import APIRouter, Request, Query
# import func from services
from Database_Connection.Redis import RedisConnection
from Services.path_service import find_path_between_stops, find_closest_stops
from typing import Optional
import json
router = APIRouter()

redis = RedisConnection.get_redis()

@router.get("/find", tags=["Journey"])
async def find_path(start_latitude: float,start_longitude:float,end_latitude:float, end_longitude:float, time:str,request: Request):
    """
    Find the path between two stops given the start and end coordinates and the time of travel.
    **Note the time format should be of 'XX:XX:XX'**. <br>
    As an example you can use the following coordinates:
    ```
    start_latitude = 48.786570
    start_longitude = 2.351090
    end_latitude = 48.860600
    end_longitude = 2.349340
    time = '08:00:00'
    ```
    """

    # Check if the search key exists in the cache (redis)
    search_key = f"{start_latitude},{start_longitude},{end_latitude},{end_longitude},{time}"

    # If the search key exists, return the result from the cache
    if redis.exists(search_key):
        paths = redis.get(search_key)
        return json.loads(paths)

    # Find the closest stops to the start and end coordinates (using the lat and lon of the stops and the user input)
    startStops = find_closest_stops(start_latitude,start_longitude)
    endStops = find_closest_stops(end_latitude,end_longitude)

    # Run a for loop to find the path between 5 closest start stops and 5 closest end stops
    all_paths = []

    # If the start or end stops are not found, return failure
    if startStops is None or endStops is None:
        return {"message": "Failed to find closest stops"}
    
    # Looping
    for st_stop in startStops:
        start = st_stop['stop_id']
        for en_stop in endStops:
            end = en_stop['stop_id']

            # Find path and journey time between stops
            path, journey_time = find_path_between_stops(start, end,time)
            if path is not None:
                all_paths.append({"path": path, "journey_time": f"{journey_time} mins"})

    # Sort the paths by length (shortest path first)
    all_paths.sort(key=lambda x: len(x))

    
    # If no paths were found, return failure
    if all_paths is None:
        return {"message": f"Sorry no path was found between ${start} and ${end}"}
    
    # If paths were found, store the search and result in the cache with the user id part of the key
    user_id = request.state.user_id
    if user_id is None:
        return {"message": "Session not established. Please provide a user_id in the header."}

    # Store the search key in the recent searches list (by user id to fetch later)
    redis.lpush(f"{user_id}-recent_searches", search_key)

    # Trim the list to keep only the 5 most recent searches
    redis.ltrim(f"{user_id}-recent_searches", 0, 4)

    # Store the search result in the cache with a timeout of 30 minutes (this is a shared pool of cache for all users, so any similar search with be fetched from the cache)
    redis.setex(search_key,1800, json.dumps(all_paths))

    return all_paths

@router.get("/find/closest", tags=["Journey"])
async def find_closest(lat: float, lon: float, request: Request):
    """
    Find the closest stops to the given coordinates. (used to find the closest stops to the user's location)
    For example, you can use the following coordinates:
    lat = 48.786570
    lon = 2.351090
    """

    # Check if the search key exists in the cache (redis)
    search_key = f"{lat},{lon}"

    # If the search key exists, return the result from the cache
    if redis.exists(search_key):
        station = redis.get(search_key)
        return json.loads(station)
    
    # Find the closest stops to the given coordinates
    closest_stops = find_closest_stops(lat, lon)

    # If the closest stops are not found, return failure
    if closest_stops is None:
        return {"message": "Failed to find closest stops"}
    

    # If closest stops were found, store the search and result in the cache with the user id part of the key
    user_id = request.state.user_id
    if user_id is None:
        return {"message": "Session not established. Please provide a user_id in the header."}


    # Store the search key in the recent searches list (by user id to fetch later)
    redis.lpush(f"{user_id}-recent_stations", search_key)

    # Trim the list to keep only the 5 most recent searches
    redis.ltrim(f"{user_id}-recent_stations", 0, 4)

    # Store the search result in the cache with a timeout of 30 minutes (this is a shared pool of cache for all users, so any similar search with be fetched from the cache)
    redis.setex(search_key,1800, json.dumps(closest_stops))
    
    return closest_stops


@router.get("/find/recent", tags=["Journey"])
async def get_recent_searches(request: Request):
    """
    Get the 5 most recent searches made by the user, and get the respective results from the cache. (which will be stored for 30 minutes)
    """
    user_id = request.state.user_id
    if user_id is None:
        return {"message": "Session not established. Please provide a user_id in the header."}
    recent_searches = redis.get(f"{user_id}-recent_searches")
    recent_stations = redis.get(f"{user_id}-recent_stations")

    recent_output = []

    # Run a loop to find the results of the recent searches and stations
    for search in recent_searches:
        search_key = search.decode()
        search_result = redis.get(search_key)

        # If the search result is not found, return a message
        if search_result is None:
            search_result = "The search has expired. Please search again."

        # Append the search and result to the output list
        recent_output.append({"search": search_key, "result": search_result})

    for station in recent_stations:
        station_key = station.decode()
        station_result = redis.get(station_key)

        # If the station result is not found, return a message
        if station_result is None:
            station_result = "The search has expired. Please search again."

        # Append the search and result to the output list
        recent_output.append({"search": station_key, "result": station_result})

    
    return {"recent_searches": [search.decode() for search in recent_searches],"recent_stations": [search.decode() for search in recent_stations] ,"results": recent_output}


# Clear recent searches
@router.get("/clear_recent", tags=["Journey"])
async def clear_recent_searches(request: Request):
    """
    Clear the recent searches made by the user. (clears the recent searches and stations)
    """

    user_id = request.state.user_id
    if user_id is None:
        return {"message": "Session not established. Please provide a user_id in the header."}
    
    # Clear the recent searches and stations from redis
    redis.delete(f"{user_id}-recent_searches")
    redis.delete(f"{user_id}-recent_stations")
    return {"message": "Recent searches cleared."}