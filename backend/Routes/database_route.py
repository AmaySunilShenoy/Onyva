from fastapi import APIRouter
# import func from services
from Services.database_service import initialize_database
from Database_Connection.Neo4j import Neo4jConnectionManager
import pandas as pd

router = APIRouter()


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


