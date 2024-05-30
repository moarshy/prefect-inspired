# surrealdb_client.py
from surrealdb import Surreal
import asyncio

DB_URL = "http://localhost:8000/rpc"
DB_NAMESPACE = "namespace"
DB_DATABASE = "database"
DB_USERNAME = "username"
DB_PASSWORD = "password"

async def get_db():
    db = Surreal(DB_URL)
    await db.signin({"user": DB_USERNAME, "pass": DB_PASSWORD})
    await db.use(DB_NAMESPACE, DB_DATABASE)
    return db
