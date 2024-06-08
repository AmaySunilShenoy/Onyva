from fastapi import FastAPI
import uvicorn
from Database_Connection.Redis import connect_to_redis
from Database_Connection.Neo4j import Neo4jConnectionManager
from Database_Connection.MongoDB import MongoDB_Connection

# ROUTES
from Routes.database_route import router as database_router
from Routes.path_route import router as path_router

app = FastAPI()

# Include routers
app.include_router(database_router, prefix="/database")
app.include_router(path_router, prefix="/path")
# Connecting to databases
redis = connect_to_redis()
mongo_db = MongoDB_Connection()
neo4j = Neo4jConnectionManager().verify_connection()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
