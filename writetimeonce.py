import os
from datetime import datetime, timezone

TIMESTAMP_LOG = "./.last_sync_time"
os.makedirs(os.path.dirname(TIMESTAMP_LOG), exist_ok=True)
with open(TIMESTAMP_LOG, "w") as f:
    f.write(datetime.now(tz=timezone.utc).isoformat())
    print(datetime.now(tz=timezone.utc).isoformat())
