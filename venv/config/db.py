from pymongo import MongoClient

# Create a connection to the MongoDB server
conn = MongoClient('mongodb://localhost:27017/')  # Adjust the URI as needed

db = conn.local  # Use 'local' as the database
users_collection = db.user  # The collection where users are stored