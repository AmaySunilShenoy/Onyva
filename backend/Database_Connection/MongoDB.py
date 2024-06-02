import pymongo


def MongoDB_Connection():
    # Connect to MongoDB
    mongo_client = pymongo.MongoClient("mongodb://mongodb:27017/")
    # Replace "mydatabase" with your database name
    mongo_db = mongo_client["mydatabase"]

    return mongo_db

