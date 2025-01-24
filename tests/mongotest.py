from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = f"mongodb+srv://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@{os.environ.get('MONGO_CLUSTER_URL')}/?retryWrites=true&w=majority&appName={os.environ.get('MONGO_APP_NAME')}"

# Create a client
client = MongoClient(connection_string)

# Access a database
db = client["socksai-db"]  # Replace 'test_database' with your database name

# Access a collection
collection = db[
    "test_collection"
]  # Replace 'test_collection' with your collection name

# Insert a document for testing
sample_document = {"name": "Test", "value": 123}
collection.insert_one(sample_document)

# Fetch the document
retrieved_document = collection.find_one({"name": "Test"})
print("Retrieved Document:", retrieved_document)
