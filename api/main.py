from datetime import UTC, datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import logging
import os
import redis
import psycopg
from shared.event import Event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_connection = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
)

postgres_connection = psycopg.connect(
    f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')} host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')}"
)

app = FastAPI(
    title="spectrvm API",
    description="Provides endpoints for clients to post their events to, and for their dashboard to retrieve them.",
    version="0.1.0",
    contact={"name": "Admin", "email": "samy.ponsar@proton.me"},
)

class EventCreate(BaseModel):
    tenant_id: str = Field(..., max_length=64)
    event_type: str = Field(..., max_length=128)
    payload: Optional[dict] = None
    metadata: Optional[dict] = None


@app.post("/v1/events")
def push_event(body: EventCreate):
    try:
        event = Event(
            tenant_id=body.tenant_id,
            event_type=body.event_type,
            received_at=datetime.now(UTC),
            payload=body.payload,
            metadata=body.metadata,
        )
    except Exception as e:
        logger.error(f"{e}")
        raise HTTPException(status_code=422, detail=str(e))
    try:
        redis_connection.lpush("events", event.model_dump_json())
        return event
    except Exception as e:
        logger.error(f"{e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again.")


@app.get("/v1/events")
def get_events(
    tenant_id: str = Query(..., max_length=64),
    event_type: Optional[str] = Query(None, max_length=128),
    count: int = Query(10, ge=1, le=100),
):
    try:
        query = "SELECT * FROM events WHERE tenant_id = %s"
        params = [tenant_id]
        if event_type:
            query += " AND event_type = %s"
            params.append(event_type)
        query += " ORDER BY received_at DESC LIMIT %s"
        params.append(count)
        with postgres_connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = []
            for row in rows:
                event_dict = dict(zip(columns, row))
                try:
                    validated = Event(**event_dict)
                    result.append(validated.model_dump())
                except Exception as e:
                    logger.critical(f"Event with id {event_dict.id} failed pydantic validation.")
                    continue
            return result
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again.")


@app.get("/health")
def health():
    redis_connected = redis_connection.ping()
    postgres_connected = not postgres_connection.closed
    if redis_connected and postgres_connected:
        return {"status": "ok"}
    raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again.")
