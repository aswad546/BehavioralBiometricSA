# worker/config.py
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vv8_backend")
DB_USER = os.getenv("DB_USER", "vv8")
DB_PASSWORD = os.getenv("DB_PASSWORD", "vv8")

DB_WRITE_MODE = os.getenv("DB_WRITE_MODE", "batch")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "job_queue")

# Paths to API definitions (if needed)
FP_APIS_PATH = os.getenv("FP_APIS_PATH", "/app/worker/target_apis/fp_apis.txt")
BEHAVIOR_APIS_PATH = os.getenv("BEHAVIOR_APIS_PATH", "/app/worker/target_apis/behavior_apis.txt")

def load_api_sources():
    with open(FP_APIS_PATH, 'r') as file:
        browser_fingerprinting_sources = {line.strip() for line in file if line.strip()}
    with open(BEHAVIOR_APIS_PATH, 'r') as file:
        behavioral_sources = {line.strip() for line in file if line.strip()}
    return browser_fingerprinting_sources, behavioral_sources

BROWSER_FINGERPRINTING_SOURCES, BEHAVIORAL_SOURCES = load_api_sources()

# Known sinks and important events
KNOWN_SINKS = [
    'Window.sessionStorage', 'MessagePort.postMessage', 'WebSocket.send', 'ServiceWorker.postMessage',
    'Window.localStorage', 'Window.openDatabase', 'XMLHttpRequest.send', 'IDBObjectStore.put',
    'RTCDataChannel.send', 'Client.postMessage', 'Window.postMessage', 'Window.indexedDB',
    'Navigator.sendBeacon', 'DedicatedWorkerGlobalScope.postMessage', 'IDBObjectStore.add',
    'Worker.postMessage', 'Document.cookie', 'HTMLInputElement.value', 'Node.textContent',
    'HTMLScriptElement.setAttribute', 'HTMLScriptElement.src', 'HTMLImageElement.src'
]

IMPORTANT_EVENTS = [
    'focus', 'blur', 'click', 'copy', 'paste', 'dblclick', 'devicemotion', 'deviceorientation',
    'keydown', 'keypress', 'keyup', 'mousedown', 'mouseenter', 'mouseleave', 'mousemove',
    'mouseup', 'orientationchange', 'pointerdown', 'pointermove', 'scroll', 'touchstart',
    'touchend', 'touchmove', 'wheel'
]
