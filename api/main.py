from datetime import UTC, datetime
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import logging
import os
import redis
import redis.retry
import psycopg
import psycopg.pool

from shared.event import Event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUIRED_ENV = [
    "REDIS_HOST",
    "REDIS_PORT",
    "REDIS_USER",
    "REDIS_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
]
for var in REQUIRED_ENV:
    if not os.getenv(var):
        raise RuntimeError(f"Missing required environment variable: {var}")

REDIS_RETRY = redis.retry.Retry(backoff=redis.backoff.exponential, retries=3)
REDIS_CONNECTION = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    retry=REDIS_RETRY,
    socket_timeout=5,
    socket_connect_timeout=5,
)

POSTGRES_POOL = psycopg.pool.ConnectionPool(
    conninfo=(
        f"dbname={os.getenv('POSTGRES_DB')} "
        f"user={os.getenv('POSTGRES_USER')} "
        f"password={os.getenv('POSTGRES_PASSWORD')} "
        f"host={os.getenv('POSTGRES_HOST')} "
        f"port={os.getenv('POSTGRES_PORT')}"
    ),
    min_size=2,
    max_size=10,
    connect_timeout=5,
    timeout=10,
)

app = FastAPI(
    title="stratvm API",
    description="Provides endpoints for clients to post their events to, and for their dashboard to retrieve them.",
    version="0.1.0",
    contact={"name": "Admin", "email": "samy.ponsar@proton.me"},
)


def api_key_required(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="API key required")
    expected = os.getenv("API_KEY")
    if credentials.credentials == expected:
        return credentials.credentials
    raise HTTPException(status_code=401, detail="Invalid API key")


class EventCreate(BaseModel):
    tenant_id: str = Field(..., max_length=64)
    event_type: str = Field(..., max_length=128)
    payload: Optional[dict] = None
    metadata: Optional[dict] = None


@app.post("/v1/events", status_code=201)
def push_event(body: EventCreate, _=Depends(api_key_required)):
    try:
        event = Event(
            tenant_id=body.tenant_id,
            event_type=body.event_type,
            received_at=datetime.now(UTC),
            payload=body.payload,
            metadata=body.metadata,
        )
    except Exception as e:
        logger.error(f"Event validation failed: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    try:
        REDIS_CONNECTION.lpush("events", event.model_dump_json())
        return event
    except Exception as e:
        logger.error(f"Failed to push event to Redis: {e}")
        raise HTTPException(
            status_code=503, detail="Service temporarily unavailable. Please try again."
        )


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
        with POSTGRES_POOL.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                result = []
                for row in rows:
                    event_dict = dict(zip(columns, row))
                    validated = Event(**event_dict)
                    result.append(validated.model_dump())
                return result
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        raise HTTPException(
            status_code=503, detail="Service temporarily unavailable. Please try again."
        )


@app.get("/readyz")
def readyz():
    try:
        redis_connected = REDIS_CONNECTION.ping()
    except redis.exceptions.RedisError:
        redis_connected = False
    postgres_connected = False
    try:
        with POSTGRES_POOL.connection() as conn:
            conn.execute("SELECT 1")
            postgres_connected = True
    except Exception:
        pass

    if redis_connected and postgres_connected:
        return {"status": "ok"}
    raise HTTPException(
        status_code=503, detail="Service temporarily unavailable. Please try again."
    )


@app.get("/livez")
def livez():
    return {"status": "ok"}
