#used by n8n
from fastapi import FastAPI, Request
from pydantic import BaseModel
from TaskAgent.task_utils import add_task, update_task, delete_task, list_tasks, clean_message
from TaskAgent.tasks import parse_interval, parse_time_of_day
import uvicorn

app = FastAPI(title="Task Agent for Scheduler API")

class TaskInput(BaseModel):
    name: str
    message: str = ""
    interval: str = None  # e.g., "30min"
    time_of_day: str = None  # e.g., "07:00"
    repeat: bool = True

@app.post("/add-task")
def api_add_task(task: TaskInput):
    interval_sec = parse_interval(f"in {task.interval}") if task.interval else None
    time_of_day = parse_time_of_day(task.time_of_day) if task.time_of_day else None
    if interval_sec and interval_sec < 60:
        interval_sec = None
    add_task(task.name, interval_sec, task.message, task.repeat, time_of_day)
    return {"status": "success", "task": task.name}

@app.post("/update-task")
def api_update_task(task: TaskInput):
    interval_sec = parse_interval(f"in {task.interval}") if task.interval else None
    time_of_day = parse_time_of_day(task.time_of_day) if task.time_of_day else None
    if interval_sec and interval_sec < 60:
        interval_sec = None
    update_task(task.name, interval_sec, task.message, time_of_day)
    return {"status": "updated", "task": task.name}

@app.delete("/delete-task/{name}")
def api_delete_task(name: str):
    delete_task(name)
    return {"status": "deleted", "task": name}

@app.get("/list-tasks")
def api_list_tasks():
    tasks = list_tasks()
    return {"tasks": tasks}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("task_api:app", host="0.0.0.0", port=2702, reload=True)
