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
    "e2e_count_total": {},
    "e2e_latency_total": {},
}

db = {}
idx = 0

def stack_metrics():
    if len(db.keys()) == 0: return

    ids = []
    for id, value in db.items():
        if "diff_ms" in value:
            path = str(value["path"])
            key = value["key"]
            if key not in metrics["e2e_count_total"]:
                metrics["e2e_count_total"][key] = defaultdict(int)
            if key not in metrics["e2e_latency_total"]:
                metrics["e2e_latency_total"][key] = defaultdict(float)
            metrics["e2e_count_total"][key][path] += 1
            metrics["e2e_latency_total"][key][path] += value["diff_ms"]
            ids.append(id)
    for id in ids:
        del db[id]

set_interval(stack_metrics, 1)


app = FastAPI(title="SFC E2E Collector", root_path=os.getenv("ROOT_PATH", default=None))



class EndRequest(BaseModel):
    id: str

class StartRequest(BaseModel):
    path: List[str]
    end_url: str
    key: str

@app.post("/start")
def post_start(file: UploadFile = File(...), req: StartRequest = Depends()):
    global idx
    idx += 1
    id = idx

    req.path = req.path[0].split(",")

    msg = '{{ "target_url": "{}","message": {{ "id": {} }} }}'.format(req.end_url, id)

    for target_url in req.path[:0:-1]:
        msg = '{{"target_url": "{}", "message": {{ "next": {} }} }}'.format(target_url, msg)
    msg = '{{"next": {} }}'.format(msg)
    
    db[id] = { "start_time": datetime.now(), "path": req.path, "key": req.key }
    
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
    for name, key_and_pathValue in metrics.items():
        for key, path_and_value in key_and_pathValue.items():
            for path, value in path_and_value.items():
                result += '{}{{key="{}", path="{}"}} {}\n'.format(name, key, path, value)
    return result

@app.get("/metrics/{key}")
def get_metrics_by_key(key: str):
    latency = 0
    cnt = 0
    for name, key_and_pathValue in metrics.items():
        for k, path_and_value in key_and_pathValue.items():
            if key != k:
                continue
            for _, value in path_and_value.items():
                if name == "e2e_count_total":
                    cnt += value
                if name == "e2e_latency_total":
                    latency += value
    return { "latency": latency, "count": cnt }

@app.delete("/metrics")
def delete_all_metrics():
    global metrics
    metrics = {
        "e2e_count_total": {},
        "e2e_latency_total": {},
    }

@app.delete("/metrics/{key}")
def delete_metrics_by_key(key: str):
    if key in metrics["e2e_count_total"].keys():
        del metrics["e2e_count_total"][key]
    if key in metrics["e2e_latency_total"].keys():
        del metrics["e2e_latency_total"][key]

@app.get("/")
def root():
    return "SFC E2E Collector"
