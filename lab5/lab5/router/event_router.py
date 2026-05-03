# File: router/event_router.py
import os
import json
import time
import redis
import requests

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
STREAM_NAME = "events"

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# Routing Table: Maps event types to destination URLs
routes = {
    "image.uploaded": [
        "http://image-resizer:5000/resize",
        "http://notifier:5000/notify"
    ]
}

print("Event Router started. Waiting for events...", flush=True)

last_id = "0-0"
while True:
    try:
        # Read new events from the stream
        events = r.xread({STREAM_NAME: last_id}, block=5000, count=10)
        if not events:
            continue

        for stream_name, messages in events:
            for message_id, message_data in messages:
                last_id = message_id
                payload = message_data.get("payload")
                if not payload:
                    continue

                event = json.loads(payload)
                event_type = event.get("event_type")
                print(f"Received event: {event_type}", flush=True)

                # Find destinations for this event type
                destinations = routes.get(event_type, [])
                
                for destination in destinations:
                    try:
                        start = time.time()
                        # Forward the event via HTTP POST
                        response = requests.post(destination, json=event, timeout=30)
                        duration_ms = round((time.time() - start) * 1000, 2)
                        print(f"Sent to {destination} | Status: {response.status_code} | {duration_ms}ms", flush=True)
                    except Exception as e:
                        print(f"Error sending event to {destination}: {e}", flush=True)
                        
    except Exception as main_error:
        print(f"Router error: {main_error}", flush=True)
        time.sleep(3)