from fastapi import FastAPI
import uvicorn
from Database_Connection.Redis import RedisConnection
from Database_Connection.Neo4j import Neo4jConnectionManager
from Database_Connection.MongoDB import MongoDBConnection
from fastapi.middleware.cors import CORSMiddleware
# ROUTES
from Routes.database_route import router as database_router
from Routes.path_route import router as path_router
from Routes.subscription_route import router as subscription_router
from Routes.auth_route import router as auth_router
from Routes.user_route import router as user_router

# JWT
from utils.JWTHandler import JWT

app = FastAPI()

jwt = JWT()


# Connecting to databases
mongo_db = MongoDBConnection()
try:
    mongo_db.connect()
    Neo4jConnectionManager().verify_connection()
    RedisConnection().get_redis()
except Exception as e:
    # This will print sometimes since the web server starts before the database is ready (docker-compose issue)
    print(f'Error connecting to database: {str(e)}')



# Add middleware to allow CORS (will be implemented in the frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware to add user_id to the request by decoding the JWT token
@app.middleware("http")
async def add_user_id(request, call_next):
    token = request.headers.get("Authorization")
    if not token:
        user_id = 'guest' + str(request.client.host)
        # remove the bearer from the token
    else:
        token = token.split(" ")[1]
        user_id = jwt.get_user_id(token)
    request.state.user_id = user_id
    response = await call_next(request)
    return response


# Include routers with different prefixes
app.include_router(database_router, prefix="/database")
app.include_router(path_router, prefix="/path")
app.include_router(subscription_router, prefix="/ligne")
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")



# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
