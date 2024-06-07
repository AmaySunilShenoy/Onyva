from fastapi import FastAPI
import uvicorn
from Database_Connection.Redis import connect_to_redis
from Database_Connection.Neo4j import Neo4jConnectionManager
from Database_Connection.MongoDB import MongoDBConnection



# ROUTES
from Routes.database_route import router as database_router
from Routes.auth_route import router as auth_router

app = FastAPI()



# Include routers
app.include_router(database_router, prefix="/database")
app.include_router(auth_router, prefix="/auth")

# Connecting to databases
redis = connect_to_redis()
mongo_db = MongoDBConnection()
try:
    mongo_db.connect()
except:
    print(f'Error connecting to MongoDB: {str(e)}')
    raise SystemExit("Failed to connect to MongoDB")



@app.on_event("startup")
async def startup_event():
    if not Neo4jConnectionManager.verify_connection():
        print("Exiting due to Neo4j connection failure.")
        raise SystemExit("Failed to connect to Neo4j")
    if not mongo_db.verify_connection():
        print("Exiting due to MongoDB connection failure.")
        raise SystemExit("Failed to connect to MongoDB")
    
    


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
