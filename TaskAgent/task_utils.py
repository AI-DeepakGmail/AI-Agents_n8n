# TaskAgent/task_utils.py
import json, time, threading, os, re
from datetime import datetime, timedelta
from Shared.utils.config import TASK_FILE

# ✅ Global task store
tasks_by_user = {}

def load_tasks():
    global tasks_by_user
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE) as f:
            data = json.load(f)
            if isinstance(data, dict):
                tasks_by_user = data
                print(f"📂 Loaded tasks from {os.path.abspath(TASK_FILE)}")
            else:
                print(f"❌ Invalid task file format — expected dict, got {type(data)}")
                tasks_by_user = {}
    else:
        tasks_by_user = {}
        print(f"📁 No existing task file found. Starting fresh.")

# ✅ Load tasks at module level
load_tasks()

def save_tasks():
    global tasks_by_user
    try:
        os.makedirs(os.path.dirname(TASK_FILE), exist_ok=True)
        with open(TASK_FILE, "w") as f:
            json.dump(tasks_by_user, f, indent=2)
        print(f"✅ Saved tasks to {os.path.abspath(TASK_FILE)}")
    except Exception as e:
        print(f"❌ Failed to save tasks: {e}")

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

def add_task(user_id, name, interval=None, message="", repeat=True, time_of_day=None):
    global tasks_by_user
    if not isinstance(tasks_by_user, dict):
        print("❌ tasks_by_user is not a dict — resetting")
        tasks_by_user = {}

    if not user_id:
        print("❌ Missing user_id — cannot save task")
        return

    if time_of_day:
        interval = None

    next_run = compute_next_run(interval, time_of_day)
    user_tasks = tasks_by_user.setdefault(user_id, [])

    for t in user_tasks:
        if t["name"] == name and t["message"] == message:
            print(f"⚠️ Duplicate task skipped for user: {user_id}")
            return

    task = {
        "name": name,
        "interval": interval,
        "time_of_day": time_of_day,
        "message": message,
        "repeat": repeat,
        "next_run": next_run
    }

    user_tasks.append(task)
    print(f"🧠 Task added for user: {user_id} → {name}")
    save_tasks()

def update_task(user_id, name, interval=None, message=None, time_of_day=None):
    global tasks_by_user
    user_tasks = tasks_by_user.get(user_id, [])
    for t in user_tasks:
        if t["name"] == name:
            if time_of_day:
                t["interval"] = None
                t["time_of_day"] = time_of_day
            else:
                t["interval"] = interval
            if message:
                t["message"] = message
            t["next_run"] = compute_next_run(t.get("interval"), t.get("time_of_day"))
            print(f"🔄 Task updated for user: {user_id} → {name}")
            save_tasks()
            return

def delete_task(user_id, name):
    global tasks_by_user
    tasks_by_user[user_id] = [t for t in tasks_by_user.get(user_id, []) if t["name"] != name]
    print(f"🗑️ Task deleted for user: {user_id} → {name}")
    save_tasks()

def list_tasks(user_id):
    global tasks_by_user
    return tasks_by_user.get(user_id, [])

def clean_message(msg):
    msg = msg.split("##OUTPUT")[-1] if "##OUTPUT" in msg else msg
    msg = re.sub(r"You are a helpful assistant.*?task:.*?\n", "", msg, flags=re.IGNORECASE | re.DOTALL)
    return msg.strip()

def send_reminder(task):
    message = clean_message(task["message"])
    print(f"\n🔔 Reminder: {message}\n>> ", end="", flush=True)

def run_scheduled_tasks():
    global tasks_by_user
    while True:
        now = time.time()
        for user_id, user_tasks in tasks_by_user.items():
            for task in user_tasks:
                if now >= task.get("next_run", 0):
                    threading.Thread(target=send_reminder, args=(task,), daemon=True).start()
                    if task.get("repeat", True):
                        task["next_run"] = compute_next_run(task.get("interval"), task.get("time_of_day"))
                    else:
                        task["next_run"] = float("inf")
        save_tasks()
        time.sleep(1)

def parse_interval(text):
    match = re.search(r"(in|every)?\s*(\d+)\s*(s|sec|secs|seconds|m|min|mins|minutes|h|hr|hrs|hours)?", text)
    if not match:
        return None
    value = int(match.group(2))
    unit = match.group(3) or "s"
    unit = unit.lower()
    if unit.startswith("s"):
        return value
    elif unit.startswith("m"):
        return value * 60
    elif unit.startswith("h"):
        return value * 3600
    return None

def parse_time_of_day(text):
    match = re.search(r"(?<!\d)(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    meridian = match.group(3)
    if meridian:
        meridian = meridian.lower()
        if meridian == "pm" and hour < 12:
            hour += 12
        elif meridian == "am" and hour == 12:
            hour = 0
    if hour > 23 or minute > 59:
        return None
    return f"{hour:02d}:{minute:02d}"
