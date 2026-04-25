from datetime import datetime
from typing import Annotated, Optional, Set
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import json
import logging
import os
import redis
import psycopg
import uuid
from shared.event import Event

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


class EventCreate(BaseModel):
    tenant_id: str = Field(..., max_length=64)
    event_type: str = Field(..., max_length=128)
    payload: Optional[dict] = None
    metadata: Optional[dict] = None


@app.post("/api/v1/events")
def push_event(body: EventCreate):
    event = Event(
        tenant_id=body.tenant_id,
        event_type=body.event_type,
        received_at=datetime.utcnow(),
        success=True,
        payload=body.payload,
        metadata=body.metadata,
    )
    try:
        redis_connection.lpush(f"{body.tenant_id}:events", event.model_dump_json())
        return event
    except Exception as e:
        raise HTTPException(status_code=500, detail="Service temporarily unavailable. Please try again.")


@app.get("/api/v1/events")
def get_events(
    tenant_id: str = Query(..., max_length=64),
    event_type: Optional[str] = Query(None, max_length=128),
    count: int = Query(10, ge=1, le=100),
):
    try:
        query = f"SELECT * FROM events " + \
            f"WHERE tenant_id = '{tenant_id}' " + \
            f"AND event_type = " + str(event_type) if event_type else "" + \
            f"ORDER BY received_at DESC LIMIT {count}"
        with postgresql_connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail="Service temporarily unavailable. Please try again.")


@app.get("/health")
def health():
    return {"status": "ok"}
