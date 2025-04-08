import pika
import time
import json
from config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE

def get_rabbitmq_connection(retries=5, delay=5):
    """Attempts to connect to RabbitMQ with retries."""
    for attempt in range(1, retries + 1):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
            )
            return connection
        except Exception as e:
            print(f"Worker: Attempt {attempt} of {retries} failed to connect to RabbitMQ: {e}")
            time.sleep(delay)
    raise Exception("Worker: Failed to connect to RabbitMQ after several attempts")

def declare_queue():
    """Ensures the queue exists (runs once at startup)."""
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    connection.close()
    print(f"Worker: Queue '{RABBITMQ_QUEUE}' declared (or already exists)")

def consume_jobs(callback):
    """Consumes jobs without re-declaring the queue every time."""
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
    print("Worker: Waiting for messages in RabbitMQ. To exit press CTRL+C")
    channel.start_consuming()
