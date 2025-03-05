# # queue_utils.py
# import json
# import redis
# from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_QUEUE_NAME

# # Create a Redis client (you may later add reconnection logic, etc.)
# redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# def push_to_queue(message: dict):
#     """Push a message (a dict) to the Redis queue."""
#     # Encode the message as JSON.
#     redis_client.rpush(REDIS_QUEUE_NAME, json.dumps(message))

# def pop_from_queue(timeout=5):
#     """Pop a message from the Redis queue, blocking for up to timeout seconds."""
#     # BLPOP returns a tuple (queue_name, message) or None on timeout.
#     item = redis_client.blpop(REDIS_QUEUE_NAME, timeout=timeout)
#     if item:
#         return json.loads(item[1])
#     return None
