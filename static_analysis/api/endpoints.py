# api/endpoints.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from multiprocessing import Manager
from db_utils import get_db_connection_context
from mq_utils import publish_job
import os
import json

router = APIRouter()

@router.post("/analyze/{script_id}")
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
        script_data = {
            "id": row[0],
            "url": row[1],
            "code": row[2],
            "APIs": row[3],  # assumes the apis column is a JSONB type, auto-converted
            "submission_id": row[4]
        }
        # Publish job to RabbitMQ so a worker can process it.
        publish_job(script_data)
        return {"status": f"Analysis job published for script_id {script_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
