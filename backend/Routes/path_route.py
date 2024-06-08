from fastapi import APIRouter
# import func from services
from Database_Connection.Neo4j import Neo4jConnectionManager
from Services.path_service import find_path_between_stops, find_closest_stops

router = APIRouter()


@router.get("/find", tags=["Path"])
# for loading the data into the Neo4j database
async def find_path(start_latitude: float,start_longitude:float,end_latitude:float, end_longitude:float, time:str):
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
    
    return all_paths

@router.get("/find/closest", tags=["Path"])
async def find_closest(lat: float, lon: float):
    closest_stops = find_closest_stops(lat, lon)
    if closest_stops is None:
        return {"message": "Failed to find closest stops"}
    return closest_stops
