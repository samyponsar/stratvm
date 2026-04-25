# Client ──POST──→ [API] ──LPUSH──→ [Redis] ──BRPOP──→ [Worker] ──INSERT──→ [PostgreSQL]
# Client ──GET───→ [API] ──SELECT──→ [PostgreSQL]

from fastapi import FastAPI, HTTPException, Query
from typing import Annotated, Set
import json
import logging
import os
import redis
import psycopg
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_connection = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
)

postgresql_connection = psycopg.connect(
    f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')} host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')}"
)

app = FastAPI(
    title="spectrvm API",
    description="Provide endpoints for clients to post their events to, and for their dashboard to retrieve them.",
    version="0.1.0",
    contact={"name": "Admin", "email": "samy.ponsar@proton.me"},
)


@app.get("/api/v1/stats")
def stats(
    log_level: Annotated[int, Query(ge=0, le=5)] = 0,
    count: Annotated[int, Query(ge=1, le=100)] = 5,
    namespaces: Annotated[Set[str], Query(max_length=10)] = None,
):
    print(namespaces)
    return {
        "log_level": log_level,
        "count": count,
        "namespaces": namespaces,
    }


@app.get("/api/v1/push_rand")
def push_rand():
    event = json.dumps({"id": str(uuid.uuid4())})
    try:
        redis_connection.lpush("client1:events", event)
        return event
    except:
        raise HTTPException(status_code=500, detail="Couldn't push to Redis queue.")


@app.get("/api/v1/get_rand")
def get_rand():
    event = json.dumps({"id": str(uuid.uuid4())})
    try:
        with postgresql_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM events LIMIT 10")
            rows = cursor.fetchall()
            return rows
    except:
        raise HTTPException(status_code=500, detail="Couldn't complete Postgres query.")


@app.get("/health")
def health():
    return {"status": "ok"}
