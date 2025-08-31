import json, time, threading, os

TASK_FILE = "data/tasks.json"
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

def add_task(name, interval, message, repeat=True):
    tasks.append({
        "name": name,
        "interval": interval,
        "message": message,
        "repeat": repeat,
        "next_run": time.time() + interval
    })
    save_tasks()

def update_task(name, interval, message=None):
    for t in tasks:
        if t["name"] == name:
            t["interval"] = interval
            if message:
                t["message"] = message
            t["next_run"] = time.time() + interval
            save_tasks()
            return

def delete_task(name):
    global tasks
    tasks = [t for t in tasks if t["name"] != name]
    save_tasks()

def list_tasks():
    return tasks

def clean_message(msg):
    # Remove prompt artifacts or verbose formatting
    if "##OUTPUT" in msg:
        msg = msg.split("##OUTPUT")[-1].strip()
    if "One possible friendly reminder" in msg:
        msg = msg.split("is:")[-1].strip()
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
                    task["next_run"] = now + task["interval"]
                else:
                    task["next_run"] = float("inf")
        save_tasks()
        time.sleep(1)
