"""
Shared dependencies — DB connections, cache, helpers
=====================================================
Used by both main.py (question graph endpoints) and
recruiter_routes.py (interview/recruiter endpoints).
"""

from typing import Dict
from neo4j import GraphDatabase
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# ── Neo4j driver (singleton) ────────────────────────────────────────
NEO4J_URI  = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", os.getenv("NEO4J_USER", "neo4j"))
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "neo4j")

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    return _driver


def get_db():
    return get_driver()


# ── MongoDB connection (singleton) ──────────────────────────────────
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB  = "interview_db"

_mongo_client = None


def get_mongo():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI)
    return _mongo_client[MONGO_DB]


def get_interviews_collection():
    return get_mongo()["interviews"]


# ── Interview question cache (in-memory, shared) ────────────────────
_interview_cache: Dict[str, dict] = {}


# ── Helper: Neo4j DateTime → Python datetime ────────────────────────
def to_native_dt(val):
    """Convert neo4j.time.DateTime → Python datetime (or return as-is / None)."""
    if val is None:
        return None
    if hasattr(val, "to_native"):
        return val.to_native()
    return val


# ── Shutdown helper ──────────────────────────────────────────────────
def shutdown_connections():
    global _driver, _mongo_client
    if _driver:
        _driver.close()
        _driver = None
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
