# config.py
import os
from dotenv import load_dotenv

# Load .env file (if present)
load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5434")
DB_NAME = os.getenv("DB_NAME", "vv8_backend")
DB_USER = os.getenv("DB_USER", "vv8")
DB_PASSWORD = os.getenv("DB_PASSWORD", "vv8")

# Write mode: either "immediate" or "batch"
DB_WRITE_MODE = os.getenv("DB_WRITE_MODE", "immediate")  # default immediate

# Redis configuration (used only for batch mode)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_QUEUE_NAME = os.getenv("REDIS_QUEUE_NAME", "db_write_queue")

# API definitions paths
FP_APIS_PATH = os.getenv("FP_APIS_PATH", "./fp_apis.txt")
BEHAVIOR_APIS_PATH = os.getenv("BEHAVIOR_APIS_PATH", "./behavior_apis.txt")

def load_api_sources():
    with open(FP_APIS_PATH, 'r') as file:
        browser_fingerprinting_sources = {line.strip() for line in file if line.strip()}
    with open(BEHAVIOR_APIS_PATH, 'r') as file:
        behavioral_sources = {line.strip() for line in file if line.strip()}
    return browser_fingerprinting_sources, behavioral_sources

BROWSER_FINGERPRINTING_SOURCES, BEHAVIORAL_SOURCES = load_api_sources()

# Known sinks and important events (unchanged)
KNOWN_SINKS = [
    'Window.sessionStorage', 
    'MessagePort.postMessage', 
    'WebSocket.send', 
    'ServiceWorker.postMessage', 
    'Window.localStorage', 
    'Window.openDatabase', 
    'XMLHttpRequest.send', 
    'IDBObjectStore.put', 
    'RTCDataChannel.send', 
    'Client.postMessage', 
    'Window.postMessage', 
    'Window.indexedDB', 
    'Navigator.sendBeacon', 
    'DedicatedWorkerGlobalScope.postMessage', 
    'IDBObjectStore.add', 
    'Worker.postMessage', 
    'Document.cookie', 
    'HTMLInputElement.value', 
    'Node.textContent',
    'HTMLScriptElement.setAttribute',
    'HTMLScriptElement.src',
    'HTMLImageElement.src'
]

IMPORTANT_EVENTS = [
    'focus', 'blur', 'click', 'copy', 'paste', 'dblclick', 'devicemotion',
    'deviceorientation', 'keydown', 'keypress', 'keyup', 'mousedown', 'mouseenter',
    'mouseleave', 'mousemove', 'mouseup', 'orientationchange', 'pointerdown',
    'pointermove', 'scroll', 'touchstart', 'touchend', 'touchmove', 'wheel',
]
