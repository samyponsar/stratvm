import redis
import psycopg
import json
import os

pod_name = os.getenv("POD_NAME")

redis_connection = redis.Redis(host='redis', port=6379, db=0)
postgres_connection = psycopg.connect("host=postgres port=5432 user=postgres connect_timeout=10")
postgres_cursor = postgres_connection.cursor()

def main():
    print("Hello!")
    while True:
        item = redis_connection.brpop('event_queue')
        entry = json.loads(item[1].decode("utf-8"))
        entry["worker"] = pod_name
        try:
            postgres_cursor.execute("INSERT INTO events (time) VALUES (%s)", (json.dumps(entry),))
            postgres_connection.commit()
        except psycopg.OperationalError:
            redis_connection.lpush('event_queue', item)
            sys.exit("Lost connection to postgres.")



if __name__ == "__main__":
    main()
