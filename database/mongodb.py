import os
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

load_dotenv()

print("Starting mongo client")
connection_string = os.getenv("MONGO_DB_CONNECTION_STRING")
mongo = MongoClient(connection_string)

prod_database = mongo[os.getenv("DB_NAME")]

# test_database is used for unit tests
test_database = mongo.aggregator_test_only
