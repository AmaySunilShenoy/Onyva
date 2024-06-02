from fastapi import FastAPI
import uvicorn
from Database_Connection.Redis import connect_to_redis
from Database_Connection.Neo4j import Neo4jConnectionManager
from Database_Connection.MongoDB import MongoDB_Connection

# ROUTES
from Routes.database_route import router as database_router

app = FastAPI()

# Include routers
app.include_router(database_router, prefix="/database")

# Connecting to databases
redis = connect_to_redis()
mongo_db = MongoDB_Connection()

@app.on_event("startup")
async def startup_event():
    if not Neo4jConnectionManager.verify_connection():
        print("Exiting due to Neo4j connection failure.")
        raise SystemExit("Failed to connect to Neo4j")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
