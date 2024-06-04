from pymongo import MongoClient

class MongoDBConnection:
    def __init__(self, host='localhost', port=27017, db_name='my_database'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(self.host, self.port)
            self.db = self.client[self.db_name]
            print('Connected to MongoDB successfully.')
        except Exception as e:
            print(f'Error connecting to MongoDB: {str(e)}')
            

    def addCollection(self, collection):
        if self.client:
            try:
                col = self.db[collection]
                print('connected to collection?')
                return col
            except Exception as e:
                print(f'error connecting to the col: {str(e)}')
            

    def close(self):
        try:
            if self.client:
                self.client.close()
                print('Connection to MongoDB closed.')
        except Exception as e:
            print(f'Error closing MongoDB connection: {str(e)}')

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
