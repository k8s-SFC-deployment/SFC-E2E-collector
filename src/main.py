import os
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict

from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.responses import PlainTextResponse

from src.utils.parsing import load_json_one_depth_v2
from src.utils.intervals import set_interval

metrics = {
    "e2e_count_total": defaultdict(int),
    "e2e_latency_total": defaultdict(float),
}

db = {}
idx = 0

def stack_metrics():
    if len(db.keys()) == 0: return

    start_id = list(db.keys())[0]
    end_id = start_id - 1
    for id, value in db.items():
        if "diff_ms" in value:
            path = str(value["path"])
            metrics["e2e_count_total"][path] += 1
            metrics["e2e_latency_total"][path] += value["diff_ms"]
            end_id = id
    for id in range(start_id, end_id + 1):
        del db[id]

set_interval(stack_metrics, 1)


app = FastAPI(title="SFC E2E Collector", root_path=os.getenv("ROOT_PATH", default=None))



class EndRequest(BaseModel):
    id: str

class StartRequest(BaseModel):
    path: List[str]
    end_url: str

@app.post("/start")
def post_start(file: UploadFile = File(...), req: StartRequest = Depends()):
    global idx
    idx += 1
    id = idx

    req.path = req.path[0].split(",")

    msg = '{{ "target_url": "{}","message": {{ "id": {} }} }}'.format(req.end_url, id)

    for target_url in req.path[:0:-1]:
        msg = '{{"next": {{"target_url": "{}", "message": {{ "next": {} }} }}}}'.format(target_url, msg)
    db[id] = { "start_time": datetime.now(), "path": req.path }
    
    target_url = req.path[0]
    data = load_json_one_depth_v2(msg, ["next"])
    files = { "file": (file.filename, file.file.read(), file.content_type) }
    
    requests.post(target_url, headers={'accept': 'application/json'}, files=files, params=data)
    return "ok"

@app.post("/end")
def post_end(file: UploadFile = File(...), req: EndRequest = Depends()):
    id = int(req.id)
    db[id]["end_time"] = datetime.now()
    db[id]["diff_ms"] = (db[id]["end_time"] - db[id]["start_time"]) / timedelta(milliseconds=1)
    
    return db[id]

@app.get("/metrics", response_class=PlainTextResponse)
def get_metrics():
    result = ""
    for name, label_and_value in metrics.items():
        for label, value in label_and_value.items():
            result += '{}{{path="{}"}} {}\n'.format(name, label, value)
    return result



@app.get("/")
def root():
    return "SFC E2E Collector"
