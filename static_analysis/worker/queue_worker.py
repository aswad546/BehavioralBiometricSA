# worker/queue_worker.py
import time
import traceback
import json
from multiprocessing import Manager
from mq_utils import get_rabbitmq_connection, consume_jobs
from db_utils import get_db_connection_context
from static_analysis import StaticAnalyzer

def wait_for_rabbitmq(timeout=60, delay=2):
    """
    Wait until a connection to RabbitMQ can be established.
    """
    start_time = time.time()
    while True:
        try:
            # Try to get a connection with a single attempt
            conn = get_rabbitmq_connection(retries=1, delay=0)
            conn.close()
            print("Worker: RabbitMQ is available.")
            break
        except Exception as e:
            if time.time() - start_time > timeout:
                raise Exception("Worker: Timeout waiting for RabbitMQ.")
            print("Worker: Waiting for RabbitMQ to become available...")
            time.sleep(delay)

def callback(ch, method, properties, body):
    try:
        # Decode the JSON message containing the script data
        script_data = json.loads(body)
        manager = Manager()
        lock = manager.Lock()
        analyzer = StaticAnalyzer(lock)
        # Process the script; submission_id is optional
        analyzer.analyze_script(
            script_data["id"],
            script_data["url"],
            script_data["code"],
            script_data["APIs"],
            script_data.get("submission_id")
        )
        # Acknowledge successful processing so the message is removed from the queue.
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("Worker: Error processing job:", e)
        traceback.print_exc()
        # Negative acknowledgement with requeue so the message is retried.
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    print("Worker: Starting RabbitMQ consumer...")
    # Wait until RabbitMQ is available before starting consumption.
    wait_for_rabbitmq(timeout=60, delay=2)
    try:
        consume_jobs(callback)
    except Exception as e:
        print("Worker: Consumer encountered an error:", e)
        traceback.print_exc()
        time.sleep(5)
        main()  # Restart the consumer loop if needed.

if __name__ == '__main__':
    main()
