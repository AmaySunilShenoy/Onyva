from pymongo import MongoClient


class MongoDBConnection:
    client = None
    db = None

    def connect(self):
        MongoDBConnection.client = MongoClient("mongodb://mongo:27017")
        MongoDBConnection.db = MongoDBConnection.client["onyva"]
        
    def verify_connection(self):
        try:
            self.connect()
            return True
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False

    def get_collection(self, collection_name):
        return MongoDBConnection.db[collection_name]

    def close(self):
        if MongoDBConnection.client:
            MongoDBConnection.client.close()