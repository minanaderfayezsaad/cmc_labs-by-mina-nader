# File: event_source/watcher.py
import os
import json
import time
import uuid
from pathlib import Path
from datetime import datetime
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
WATCH_DIR = Path(os.getenv("WATCH_DIR", "/data/input"))
STREAM_NAME = "events"

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
WATCH_DIR.mkdir(parents=True, exist_ok=True)
seen_files = set()

print(f"Event Source started. Watching folder: {WATCH_DIR}", flush=True)

def is_image(path: Path):
    return path.suffix.lower() in [".png", ".jpg", ".jpeg"]

def file_is_stable(path: Path):
    try:
        size1 = path.stat().st_size
        time.sleep(0.5)
        size2 = path.stat().st_size
        return size1 == size2
    except FileNotFoundError:
        return False

while True:
    for path in WATCH_DIR.iterdir():
        if not path.is_file():
            continue
        if not is_image(path):
            continue
        if str(path) in seen_files:
            continue
        if not file_is_stable(path):
            continue

        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "image.uploaded",
            "file_name": path.name,
            "file_path": str(path),
            "width": 300,
            "created_at": datetime.now().isoformat()
        }

        r.xadd(STREAM_NAME, {"payload": json.dumps(event)})
        seen_files.add(str(path))
        print("Published event:", json.dumps(event, indent=2), flush=True)
    
    time.sleep(2)