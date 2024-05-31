from fastapi import FastAPI
from redis import Redis
from neo4j import GraphDatabase
import pymongo

app = FastAPI()

# Connect to Redis
redis = Redis(host="redis", port=6379, decode_responses=True)

# Connect to MongoDB
mongo_client = pymongo.MongoClient("mongodb://mongodb:27017/")
mongo_db = mongo_client["mydatabase"]  # Replace "mydatabase" with your database name

# Connect to Neo4j
neo4j_uri = "neo4j://neo4j"
neo4j_auth = ("neo4j", "password")

def verify_neo4j_connection():
    try:
        with GraphDatabase.driver(neo4j_uri, auth=neo4j_auth) as driver:
            driver.verify_connectivity()
            return True
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        return False

# API Endpoints
@app.get("/", tags=["Users"])
async def hello():
    return {"success": True}

if __name__ == "__main__":
    # Verify Neo4j connection
    if verify_neo4j_connection():
        # Run FastAPI server
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("Exiting due to Neo4j connection failure.")
