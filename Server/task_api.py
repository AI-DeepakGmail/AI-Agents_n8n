# Server/task_api.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from TaskAgent.task_utils import (
    update_task, delete_task, list_tasks, parse_interval, parse_time_of_day
)
from TaskAgent.task_parser import handle_task_command

app = FastAPI(title="Task Agent for Scheduler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskInput(BaseModel):
    user_id: str
    name: str
    message: str = ""
    interval: str | None = None
    time_of_day: str | None = None
    repeat: bool = True

class RawText(BaseModel):
    user_id: str
    text: str
    context: dict | None = None

@app.post("/parse-task")
def api_parse_task(payload: RawText):
    result = handle_task_command(payload.text, context=payload.context, user_id=payload.user_id)
    return result

@app.post("/update-task")
def api_update_task(task: TaskInput):
    interval_sec = parse_interval(f"in {task.interval}") if task.interval else None
    time_of_day = parse_time_of_day(task.time_of_day) if task.time_of_day else None
    if interval_sec and interval_sec < 60:
        interval_sec = None
    update_task(task.user_id, task.name, interval_sec, task.message, time_of_day)
    return {"status": "updated", "task": task.name}

@app.delete("/delete-task/{user_id}/{name}")
def api_delete_task(user_id: str, name: str):
    delete_task(user_id, name)
    return {"status": "deleted", "task": name}

@app.get("/list-tasks/{user_id}")
def api_list_tasks(user_id: str):
    return {"tasks": list_tasks(user_id)}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Task Agent is running"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("task_api:app", host="0.0.0.0", port=2702, reload=True)
