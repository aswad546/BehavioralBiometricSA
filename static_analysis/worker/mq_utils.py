# worker/mq_utils.py
import pika
import time
import json
from config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE

def get_rabbitmq_connection(retries=5, delay=5):
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

def consume_jobs(callback):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
    print("Worker: Waiting for messages in RabbitMQ. To exit press CTRL+C")
    channel.start_consuming()
