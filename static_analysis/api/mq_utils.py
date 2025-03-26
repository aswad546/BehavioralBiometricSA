# api/mq_utils.py
import pika
import time
import json
from config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE

# Establish a persistent RabbitMQ connection
def get_rabbitmq_connection(retries=5, delay=5):
    for attempt in range(1, retries + 1):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
            )
            return connection
        except Exception as e:
            print(f"API: Attempt {attempt} of {retries} failed to connect to RabbitMQ: {e}")
            time.sleep(delay)
    raise Exception("API: Failed to connect to RabbitMQ after several attempts")

# Declare queue only once at app startup
def declare_queue():
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    connection.close()
    print(f"Queue '{RABBITMQ_QUEUE}' declared (or already exists)")

# Publish job without re-declaring queue
def publish_job(message: dict):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistent messages
        )
    )
    connection.close()

# Pop message without re-declaring queue
def pop_from_queue(timeout=5):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    method_frame, header_frame, body = channel.basic_get(RABBITMQ_QUEUE)
    if method_frame:
        channel.basic_ack(method_frame.delivery_tag)
        connection.close()
        return json.loads(body)
    connection.close()
    return None

# Consume jobs without re-declaring queue
def consume_jobs(callback):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
    print("API: Waiting for messages in RabbitMQ. To exit press CTRL+C")
    channel.start_consuming()
