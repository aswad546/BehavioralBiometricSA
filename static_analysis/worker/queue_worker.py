# worker/queue_worker.py
import time
import traceback
import json
import multiprocessing
import threading
from mq_utils import get_rabbitmq_connection, consume_jobs, declare_queue
from static_analysis import StaticAnalyzer

def wait_for_rabbitmq(timeout=60, delay=2):
    start_time = time.time()
    while True:
        try:
            conn = get_rabbitmq_connection(retries=1, delay=0)
            conn.close()
            print("Worker: RabbitMQ is available.")
            break
        except Exception as e:
            if time.time() - start_time > timeout:
                raise Exception("Worker: Timeout waiting for RabbitMQ.")
            print("Worker: Waiting for RabbitMQ to become available...")
            time.sleep(delay)

def process_job(body, result_queue):
    """
    This function runs in a separate process (its main thread)
    so that the signal-based Timeout works properly.
    """
    try:
        # Decode the JSON message containing the script data
        script_data = json.loads(body)
        # Instantiate StaticAnalyzer. If needed, create and pass a lock.
        analyzer = StaticAnalyzer(lock=None)
        analyzer.analyze_script(
            script_data["id"],
            script_data["url"],
            script_data["code"],
            script_data["APIs"],
            script_data.get("submission_id")
        )
        # If processing completes successfully, report success.
        result_queue.put(True)
    except Exception as e:
        print("Worker: Error processing job in process:", e)
        traceback.print_exc()
        result_queue.put(False)

def run_job_in_thread(ch, method, body):
    """
    This function runs in its own thread. It spawns a new process to run the CPU-bound task.
    The blocking join call here does not affect the main thread.
    """
    result_queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=process_job, args=(body, result_queue))
    p.start()
    # Wait for the process to finish up to an outer timeout (e.g., 900 seconds)
    p.join(timeout=900)
    if p.is_alive():
        print("Worker: Process is still alive after outer timeout, terminating.")
        p.terminate()
        p.join()
        ch.connection.add_callback_threadsafe(
            lambda: ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        )
    else:
        try:
            result = result_queue.get_nowait()
        except Exception:
            result = False
        if result is True:
            ch.connection.add_callback_threadsafe(
                lambda: ch.basic_ack(delivery_tag=method.delivery_tag)
            )
        else:
            ch.connection.add_callback_threadsafe(
                lambda: ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            )

def callback(ch, method, properties, body):
    """
    RabbitMQ callback function.
    Instead of processing the job in this thread (which might block heartbeats),
    we offload it to a new thread which then spawns a process.
    """
    t = threading.Thread(target=run_job_in_thread, args=(ch, method, body), daemon=True)
    t.start()

def main():
    print("Worker: Starting RabbitMQ consumer...")
    wait_for_rabbitmq(timeout=60, delay=2)
    declare_queue()
    try:
        consume_jobs(callback)
    except Exception as e:
        print("Worker: Consumer encountered an error:", e)
        traceback.print_exc()
        time.sleep(5)
        main()  # Restart consumer loop if needed.

if __name__ == '__main__':
    main()
