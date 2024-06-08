from fastapi import APIRouter
# import func from services
from Services.database_service import initialize_database
from Database_Connection.Neo4j import Neo4jConnectionManager
import pandas as pd
from Database_Connection.Redis import RedisConnection

router = APIRouter()
redis  = RedisConnection.get_redis()

@router.get("/Neo4j/init", tags=["Database"])
# for loading the data into the Neo4j database
async def init():
    try:
        stops_df = pd.read_csv('/code/Database_Connection/DataFiles/stops.csv')
        stop_sequence_df = pd.read_csv('/code/Database_Connection/DataFiles/stops_new.csv')
        initialize_database(stops_df, stop_sequence_df)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        Neo4jConnectionManager.close()

@router.get("/Redis/init", tags=["Database"])
# for loading the data into the Redis database
# reddis wil have all the lines and the stops sequence (stop_id) using stops_new.csv and people can subscribe to a line
async def init():
  
        stop_sequence_df = pd.read_csv('/code/Database_Connection/DataFiles/stops_new.csv')
        # load the data into the redis database
        for index, row in stop_sequence_df.iterrows():
            line = row['route_id']
            line_type = row['route_type']
            stop_sequence = row['stop_order']
            redis.hmset(line, {"route_type": line_type, "stop_sequence": stop_sequence})
          
        return {"success": True}



