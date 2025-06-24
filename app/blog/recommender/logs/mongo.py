from pymongo import MongoClient, errors
from datetime import datetime
import os
from typing import List, Dict, Set

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:secret@mongo:27017/")
client = MongoClient(MONGO_URI)
db = client.blog_recommendation

reads_collection = db.reads
likes_collection = db.likes
blog_uploads_collection = db.blog_uploads_logs
blog_user_collection = db.blog_user_logs

likes_collection.create_index([("user_id", 1), ("blog_id", 1)], unique=True)

reads_collection.create_index([("user_id", 1), ("blog_id", 1)], unique=True)

blog_uploads_collection.create_index([("blog_id", 1)], unique=True)

blog_user_collection.create_index([("user_id", 1)], unique=True)


# read , like logs
def log_read_event(user_id, blog_id):
    reads_collection.update_one(
        {"user_id": user_id, "blog_id": blog_id},
        {"$set": {"timestamp": datetime.utcnow()}},
        upsert=True,
    )


def log_like_event(user_id, blog_id):
    try:
        likes_collection.insert_one(
            {"user_id": user_id, "blog_id": blog_id, "timestamp": datetime.utcnow()}
        )
    except errors.DuplicateKeyError:
        pass


def remove_like_event(user_id, blog_id):
    result = likes_collection.delete_one({"user_id": user_id, "blog_id": blog_id})
    return result.deleted_count > 0


def get_user_read_logs(user_id: str) -> List[Dict]:
    return list(
        reads_collection.find(
            {"user_id": user_id}, {"_id": 0, "blog_id": 1, "timestamp": 1}
        )
    )


def get_user_like_logs(user_id: str) -> List[Dict]:
    return list(
        likes_collection.find(
            {"user_id": user_id}, {"_id": 0, "blog_id": 1, "timestamp": 1}
        )
    )


def get_latest_interaction_timestamp(user_id):
    read = reads_collection.find_one(
        {"user_id": user_id}, sort=[("timestamp", -1)], projection={"timestamp": 1}
    )
    like = likes_collection.find_one(
        {"user_id": user_id}, sort=[("timestamp", -1)], projection={"timestamp": 1}
    )
    timestamps = []
    if read:
        timestamps.append(read["timestamp"])
    if like:
        timestamps.append(like["timestamp"])
    return max(timestamps) if timestamps else None


# pincone tracking blogs
def mark_blog_as_uploaded(blog_id):
    """Mark a blog as uploaded to Pinecone."""
    blog_uploads_collection.update_one(
        {"blog_id": str(blog_id)},
        {"$set": {"blog_id": str(blog_id), "timestamp": datetime.utcnow()}},
        upsert=True,
    )


def fetch_existing_blog_ids() -> Set[str]:
    return set(
        doc["blog_id"]
        for doc in blog_uploads_collection.find({}, {"_id": 0, "blog_id": 1})
    )


# pincone tracking user
def mark_user_as_uploaded(user_id):
    blog_user_collection.update_one(
        {"user_id": str(user_id)},
        {"$set": {"user_id": str(user_id), "uploaded_at": datetime.utcnow()}},
        upsert=True,
    )


def fetch_existing_user_ids():
    return set(
        doc["user_id"]
        for doc in blog_user_collection.find({}, {"_id": 0, "user_id": 1})
    )


def get_user_last_upload_time(user_id):
    record = blog_user_collection.find_one({"user_id": str(user_id)})
    if record and "uploaded_at" in record:
        return record["uploaded_at"]
    return None
