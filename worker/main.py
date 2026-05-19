import json
import logging
import os
import signal
import time
from datetime import UTC, datetime
from psycopg_pool import ConnectionPool
from psycopg.errors import OperationalError
import redis
import redis.retry

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

REDIS_RETRY = redis.retry.Retry(backoff=redis.backoff.ExponentialBackoff(), retries=3)
REDIS_CONNECTION = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    retry=REDIS_RETRY,
    socket_timeout=5,
    socket_connect_timeout=5,
    health_check_interval=30,
)

POSTGRES_POOL = ConnectionPool(
    conninfo=(
        f"dbname={os.getenv('POSTGRES_DB')} "
        f"user={os.getenv('POSTGRES_USER')} "
        f"password={os.getenv('POSTGRES_PASSWORD')} "
        f"host={os.getenv('POSTGRES_HOST')} "
        f"port={os.getenv('POSTGRES_PORT')}"
    ),
    min_size=2,
    max_size=10,
    reconnect_timeout=5,
    timeout=10,
)

shutdown = False


def handle_shutdown(signum, frame):
    global shutdown
    logger.info(f"Received signal {signum}, flushing pending events...")
    shutdown = True


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

pending_events = []
FLUSH_INTERVAL_SECONDS = 2

last_flush = time.monotonic()


def flush_events():
    if not pending_events:
        return

    max_retries = 3
    for attempt in range(max_retries):
        try:
            committed_at = datetime.now(UTC)
            for e in pending_events:
                e.committed_at = committed_at

            with POSTGRES_POOL.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.executemany(
                        "INSERT INTO events (tenant_id, event_type, received_at, processed_at, committed_at, payload, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
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
                    conn.commit()

            pending_events.clear()
            return

        except OperationalError as e:
            wait = min(2**attempt, 30)
            logger.warning(
                f"Postgres write failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait}s..."
            )
            time.sleep(wait)
        except Exception:
            logger.critical("Unexpected error flushing events", exc_info=True)
            pending_events.clear()
            return

    logger.error(
        f"Failed to flush {len(pending_events)} events after {max_retries} attempts"
    )
    pending_events.clear()


while not shutdown:
    if time.monotonic() - last_flush >= FLUSH_INTERVAL_SECONDS and pending_events:
        flush_events()
        last_flush = time.monotonic()

    result = REDIS_CONNECTION.brpop("events", timeout=1)
    if result:
        _, data = result
        try:
            event = Event.model_validate(json.loads(data.decode("utf-8")))
            event.processed_at = datetime.now(UTC)
            pending_events.append(event)
        except Exception as e:
            logger.critical(f"Error validating an event from Redis: {e}")

    if shutdown and pending_events:
        logger.info("Shutting down, flushing remaining events...")
        flush_events()

logger.info("Worker shut down cleanly")
