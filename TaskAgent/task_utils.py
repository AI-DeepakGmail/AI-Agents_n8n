import json, time, threading, os, re
from datetime import datetime, timedelta
from Shared.utils.config import TASK_FILE

tasks = []

def save_tasks():
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f)

def load_tasks():
    global tasks
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE) as f:
            tasks = json.load(f)
    else:
        tasks = []

def compute_next_run(interval=None, time_of_day=None):
    now = time.time()
    if interval:
        return now + interval
    elif time_of_day:
        try:
            if not re.match(r"^\d{2}:\d{2}$", time_of_day):
                return now
            hour, minute = map(int, time_of_day.split(":"))
            if hour > 23 or minute > 59:
                return now
            target = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target.timestamp() < now:
                target += timedelta(days=1)
            return target.timestamp()
        except:
            return now
    return now

def add_task(name, interval=None, message="", repeat=True, time_of_day=None):
    if time_of_day:
        interval = None
    next_run = compute_next_run(interval, time_of_day)
    tasks.append({
        "name": name,
        "interval": interval,
        "time_of_day": time_of_day,
        "message": message,
        "repeat": repeat,
        "next_run": next_run
    })
    save_tasks()

def update_task(name, interval=None, message=None, time_of_day=None):
    for t in tasks:
        if t["name"] == name:
            if time_of_day:
                t["interval"] = None
                t["time_of_day"] = time_of_day
            else:
                t["interval"] = interval
            if message:
                t["message"] = message
            t["next_run"] = compute_next_run(t.get("interval"), t.get("time_of_day"))
            save_tasks()
            return

def delete_task(name):
    global tasks
    tasks = [t for t in tasks if t["name"] != name]
    save_tasks()

def list_tasks():
    return tasks

def clean_message(msg):
    msg = msg.split("##OUTPUT")[-1] if "##OUTPUT" in msg else msg
    msg = re.sub(r"You are a helpful assistant.*?task:.*?\n", "", msg, flags=re.IGNORECASE | re.DOTALL)
    return msg.strip()

def send_reminder(task):
    message = clean_message(task["message"])
    print(f"\n🔔 Reminder: {message}\n>> ", end="", flush=True)

def run_scheduled_tasks():
    load_tasks()
    while True:
        now = time.time()
        for task in tasks:
            if now >= task.get("next_run", 0):
                threading.Thread(target=send_reminder, args=(task,), daemon=True).start()
                if task.get("repeat", True):
                    task["next_run"] = compute_next_run(task.get("interval"), task.get("time_of_day"))
                else:
                    task["next_run"] = float("inf")
        save_tasks()
        time.sleep(1)
