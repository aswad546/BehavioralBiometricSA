# api.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import json
from db_utils import get_db_connection_context
from multiprocessing import Manager
from static_analysis import StaticAnalyzer
from db_utils import create_multicore_static_info_table
import os

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
    # Read the DROP_TABLE flag from the environment; default is false.
    drop_flag = os.getenv("DROP_TABLE", "false").lower() == "true"
    create_multicore_static_info_table(drop_flag)

def process_script(script_data: dict, lock):
    analyzer = StaticAnalyzer(lock)
    analyzer.analyze_script(
        script_data["id"],
        script_data["url"],
        script_data["code"],
        script_data["APIs"],
        script_data["submission_id"]
    )

@app.post("/analyze/{script_id}")
def analyze_script_endpoint(script_id: int, background_tasks: BackgroundTasks):
    try:
        with get_db_connection_context() as conn:
            cur = conn.cursor()
            query = "SELECT id, url, code, apis, submission_id FROM script_flow WHERE id = %s;"
            cur.execute(query, (script_id,))
            row = cur.fetchone()
            cur.close()
        if row is None:
            raise HTTPException(status_code=404, detail="Script not found")
        # Build the script_data dictionary.
        script_data = {
            "id": row[0],
            "url": row[1],
            "code": row[2],
            "APIs": row[3],
            "submission_id": row[4]
            # No more count_field
        }

        manager = Manager()
        lock = manager.Lock()
        background_tasks.add_task(process_script, script_data, lock)
        return {"status": f"Analysis started for script_id {script_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
