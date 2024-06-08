from fastapi import FastAPI
import uvicorn
from Database_Connection.Redis import RedisConnection
from Database_Connection.Neo4j import Neo4jConnectionManager
from Database_Connection.MongoDB import MongoDBConnection
from fastapi.middleware.cors import CORSMiddleware
# ROUTES
from Routes.database_route import router as database_router
from Routes.path_route import router as path_router
from Routes.user_route import router as user_router
from Routes.auth_route import router as auth_router

app = FastAPI()


# Include routers
app.include_router(database_router, prefix="/database")
app.include_router(path_router, prefix="/path")
app.include_router(user_router, prefix="/user")
app.include_router(auth_router, prefix="/auth")

# Connecting to databases
neo4j = Neo4jConnectionManager().verify_connection()
redis = RedisConnection()
mongo_db = MongoDBConnection()
try:
    mongo_db.connect()
except:
    print(f'Error connecting to MongoDB: {str(e)}')
    raise SystemExit("Failed to connect to MongoDB")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as necessary for your use case
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
