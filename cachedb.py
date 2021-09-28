DB_NAME = "wanderlist"
CONNECTION_STRING = "mongodb://127.0.0.1:27017/wanderlist&replicaSet=WanMongoReplSet"

def get_db():
    from pymongo import MongoClient
    import pymongo

    # Provide the mongodb atlas url to connect python to mongodb using pymongo

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client[DB_NAME]
    
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":    
    dbname = get_db()["users"]
