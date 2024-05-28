from redis import Redis
from fastapi import FastAPI
from neo4j import GraphDatabase
import pymongo

client = pymongo.MongoClient("mongodb://mongodb:27017/")

URI = "neo4j://neo4j"
AUTH = ("neo4j", "password")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

redis = Redis(host="redis", port=6379, decode_responses=True)


tags_metadata = [
    {
        "name": "Users",
        "description": "Operations with users.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

# API Endpoints
@app.post("/", tags=["Users"])
async def hello():
    return {"success": True}
