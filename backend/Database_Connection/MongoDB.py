from pymongo import MongoClient

# Class to handle MongoDB connection and global access to the database
class MongoDBConnection:
    client = None
    db = None

    # Method to connect to our mongodb database
    def connect(self):
        MongoDBConnection.client = MongoClient("mongodb://mongo:27017")
        MongoDBConnection.db = MongoDBConnection.client["onyva"]
        

    # Method to verify if the connection is established
    def verify_connection(self):
        try:
            self.connect()
            return True
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False

    # Method to get a collection from the database (used to fetch users collection)
    def get_collection(self, collection_name):
        return MongoDBConnection.db[collection_name]

    # Method to close the connection
    def close(self):
        if MongoDBConnection.client:
            MongoDBConnection.client.close()