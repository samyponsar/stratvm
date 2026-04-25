import json
import logging
import os
from datetime import datetime

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

postgresql_connection = psycopg.connect(
    f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')} host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')}"
)

pending_events = []
MAX_PENDING_EVENTS = 10

while True:
    _, data = redis_connection.brpop("client1:events", timeout=0)
    if data:
        event = Event.model_validate(json.loads(data.decode("utf-8")))
        event.processed_at = datetime.utcnow()
        pending_events.append(event)
        logger.info(f"{len(pending_events)} pending events.")

    if len(pending_events) >= MAX_PENDING_EVENTS:
        with postgresql_connection.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO events (tenant_id, event_type, received_at, processed_at) VALUES (%s, %s, %s, %s)",
                [
                    (
                        e.tenant_id,
                        e.event_type,
                        e.received_at,
                        e.processed_at,
                    )
                    for e in pending_events
                ],
            )
        postgresql_connection.commit()
        pending_events.clear()
        logger.info("Ting")
