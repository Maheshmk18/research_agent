import os
from datetime import datetime

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DATABASE", "research_agent")


client = MongoClient(MONGO_URI)
db = client[DB_NAME]


plans_collection = db["plans"]
raw_data_collection = db["raw_data"]
reports_collection = db["reports"]
agent_logs_collection = db["agent_logs"]


def save_plan(topic: str, plan: str, status: str = "created"):
    now = datetime.utcnow()
    doc = {
        "topic": topic,
        "plan": plan,
        "status": status,
        "created_at": now,
        "updated_at": now,
    }
    return plans_collection.insert_one(doc).inserted_id


def save_raw_data(topic: str, query: str, sources: list):
    doc = {
        "topic": topic,
        "query": query,
        "sources": sources,
        "total_sources": len(sources),
        "searched_at": datetime.utcnow(),
    }
    return raw_data_collection.insert_one(doc).inserted_id


def save_report(
    topic: str,
    draft_report: str,
    final_report: str,
    status: str,
    pinecone_id: str,
    word_count: int,
):
    now = datetime.utcnow()
    doc = {
        "topic": topic,
        "draft_report": draft_report,
        "final_report": final_report,
        "status": status,
        "pinecone_id": pinecone_id,
        "word_count": word_count,
        "created_at": now,
        "verified_at": now,
    }
    return reports_collection.insert_one(doc).inserted_id


def save_agent_log(
    topic: str,
    agent_name: str,
    status: str,
    input_text: str = "",
    output_text: str = "",
    time_taken: str = "",
    error: str = "",
):
    doc = {
        "topic": topic,
        "agent_name": agent_name,
        "status": status,
        "input": input_text,
        "output": output_text,
        "time_taken": time_taken,
        "error": error,
        "timestamp": datetime.utcnow(),
    }
    return agent_logs_collection.insert_one(doc).inserted_id


def get_all_reports():
    return list(reports_collection.find().sort("created_at", -1))


def get_report_by_id(report_id):
    return reports_collection.find_one({"_id": ObjectId(report_id)})


def get_report_by_mongo_id(mongo_id: str):
    return reports_collection.find_one({"_id": ObjectId(mongo_id)})
