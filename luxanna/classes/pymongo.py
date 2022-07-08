import os
from pymongo import MongoClient


# Create a class to hold the database connection
class PyMongoManager:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.summoners_collection = self.client.get_database("main").get_collection(
            "summoners"
        )

    print("📚: Connected to Database")

    def get_user_profile(self, user_id: str) -> any:
        return self.summoners_collection.find_one({"_id": str(user_id)})

    def summoners_count(self) -> int:
        return self.summoners_collection.count_documents({})
