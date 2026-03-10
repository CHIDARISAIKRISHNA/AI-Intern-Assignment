import psutil
import time
from datetime import datetime
from db import create_db, insert_event
create_db()
print("Observer started...")

while True:
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"CPU={cpu} MEM={mem} DISK={disk}"
    severity = "LOW"
    if cpu > 85 or mem > 85 or disk > 90:
        severity = "HIGH"
    insert_event(timestamp, "psutil", severity, message)
    print("Collected:", message)
    time.sleep(5)