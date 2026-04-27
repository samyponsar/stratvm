import json
import logging
import os
import time
from datetime import UTC, datetime
import psycopg
import redis

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

pending_events = []
FLUSH_INTERVAL_SECONDS = 2

last_flush = time.time()

while True:
    _, data = redis_connection.brpop("events", timeout=0)
    if data:
        try:
            event = Event.model_validate(json.loads(data.decode("utf-8")))
            event.processed_at = datetime.now(UTC)
            pending_events.append(event)
        except Exception as e:
            logger.critical(f"Error validating an event from Redis: {e}")

    if time.time() - last_flush >= FLUSH_INTERVAL_SECONDS and pending_events:
        try:
            committed_at = datetime.now(UTC)
            for e in pending_events:
                e.committed_at = committed_at
            with postgres_connection.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO events (tenant_id, event_type, received_at, processed_at, committed_at, payload, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    [
                        (
                            e.tenant_id,
                            e.event_type,
                            e.received_at,
                            e.processed_at,
                            e.committed_at,
                            json.dumps(e.payload) if e.payload else None,
                            json.dumps(e.metadata) if e.metadata else None,
                        )
                        for e in pending_events
                    ],
                )
            postgres_connection.commit()
            pending_events.clear()
        except Exception as e:
            logger.critical(f"Error while writing to Postgres: {e}")
