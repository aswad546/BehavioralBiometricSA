# api/endpoints.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from multiprocessing import Manager
from db_utils import get_db_connection_context
from mq_utils import publish_job
import os
import json
import traceback

router = APIRouter()

from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Body
from db_utils import get_db_connection_context
from mq_utils import publish_job

router = APIRouter()

@router.post("/analyze")
def analyze_scripts_endpoint(script_ids = Body(...), background_tasks: BackgroundTasks = None):
    """
    Expects a JSON body like: [584, 585, 586]
    For each provided script_id, fetch the script data and publish a job.
    """
    published_ids = []

    print(script_ids)

    try:
        script_ids = [int(sid) for sid in script_ids]
    except ValueError as ve:
        raise HTTPException(status_code=400, detail="Invalid script_id format, expected numeric strings") from ve

    try:
        with get_db_connection_context() as conn:
            cur = conn.cursor()
            # Using PostgreSQL's ANY to query multiple IDs at once.
            query = "SELECT id, url, code, apis, submission_id FROM script_flow WHERE id = ANY(%s);"
            cur.execute(query, (script_ids,))
            rows = cur.fetchall()
            cur.close()
            
        if not rows:
            raise HTTPException(status_code=404, detail="No scripts found for the provided IDs")
        
        for row in rows:
            script_data = {
                "id": row[0],
                "url": row[1],
                "code": row[2],
                "APIs": row[3],  # Assumes apis column is a JSONB type that auto-converts.
                "submission_id": row[4]
            }
            # Publish the job to RabbitMQ (this call can also be scheduled as a background task if needed)
            publish_job(script_data)
            published_ids.append(script_data["id"])
        
        return {"status": "Analysis jobs published", "script_ids": published_ids}
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
