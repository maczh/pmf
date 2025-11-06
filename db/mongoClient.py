from pymongo import MongoClient

class mongo:
    uri = str
    db_name = str
    pool_size = int
    max_overflow = int
    client: MongoClient
    db = None
    
    def __init__(self, uri, db_name, pool_size=5, max_overflow=100):
        self.uri = uri
        self.db_name = db_name
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.client = MongoClient(self.uri,minPoolSize=self.pool_size, maxPoolSize=self.max_overflow)
        self.db = self.client[self.db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def close(self):
        self.client.close()

    def check_connection(self) -> bool:
        try:
            # The ismaster command is cheap and does not require auth.
            self.db.command('version')
            return True
        except Exception as e:
            print(f"MongoDB connection check failed: {e}")
            self.client = MongoClient(self.uri,minPoolSize=self.pool_size, maxPoolSize=self.max_overflow)
            self.db = self.client[self.db_name]
            return False