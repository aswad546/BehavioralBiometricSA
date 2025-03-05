# api/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env (placed at the project root)
load_dotenv()

# Database configuration for the API service
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vv8_backend")
DB_USER = os.getenv("DB_USER", "vv8")
DB_PASSWORD = os.getenv("DB_PASSWORD", "vv8")

# Write mode: "immediate" or "batch"
DB_WRITE_MODE = os.getenv("DB_WRITE_MODE", "immediate")

# RabbitMQ configuration (for publishing jobs)
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "job_queue")

