# queue_worker.py
import time
import traceback
from BehavioralBiometricSA.static_analysis.worker.queue_utils import pop_from_queue, redis_client
from db_utils import get_db_connection_context
import json
from config import REDIS_QUEUE_NAME

def process_queue_item(item: dict):
    """Process a single queue item by executing its insert statement."""
    try:
        # Since the statement was stored as a string, reconstruct it.
        stmt_str = item["stmt"]
        values = item["values"]
        with get_db_connection_context() as conn:
            cur = conn.cursor()
            cur.execute(stmt_str, values)
            conn.commit()
            cur.close()
        print("Batch write successful.")
    except Exception as e:
        print("Error processing queue item:", e)
        traceback.print_exc()
        # Optionally, push the item back for a retry
        # (Be careful with endless loops; you might add a retry counter.)
        redis_client.rpush(REDIS_QUEUE_NAME, json.dumps(item))
        print("Item requeued.")

def worker_loop():
    print("Redis queue worker started.")
    while True:
        item = pop_from_queue(timeout=5)
        if item is not None:
            process_queue_item(item)
        else:
            # Sleep briefly when no item is available
            time.sleep(1)

if __name__ == '__main__':
    worker_loop()
