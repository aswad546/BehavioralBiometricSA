# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from db_utils import create_multicore_static_info_table
from endpoints import router as api_router
from mq_utils import declare_queue

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    drop_flag = os.getenv("DROP_TABLE", "false").lower() == "true"
    create_multicore_static_info_table(drop_flag)
    declare_queue()  # Ensures queue is declared once at startup

app.include_router(api_router)
