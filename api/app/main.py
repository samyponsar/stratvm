from fastapi import FastAPI, HTTPException
import redis
import psycopg
import time
from datetime import datetime
import json
import os

pod_name = os.getenv("POD_NAME")

redis_connection = redis.Redis(host='redis', port=6379, db=0)
postgres_connection = psycopg.connect("host=postgres port=5432 user=postgres connect_timeout=10")
postgres_cursor = postgres_connection.cursor()

app = FastAPI()

@app.get("/")
async def root_get():
    postgres_cursor.execute("SELECT * FROM events")
    table = postgres_cursor.fetchall()
    return table

@app.post("/")
async def root_post():
    event = json.dumps({
        "time": str(datetime.now()),
        "api": pod_name
    })
    redis_connection.lpush('event_queue', event)
    return {"status": "ok"}

@app.get("/healthz")
async def healthz():
    if not redis_connection.ping():
        raise HTTPException(status_code=503, detail="Service unavailable")
    try:
        postgres_connection.cursor().execute("SELECT 1")
    except psycopg.OperationalError:
        raise HTTPException(status_code=503, detail="Service unavailable")
    return {"status": "ok"}