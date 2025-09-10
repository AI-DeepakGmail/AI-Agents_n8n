import json
import os
from datetime import datetime
from dateutil.parser import parse
#from Shared.utils.config import TASK_FILE

TASK_FILE = "task.json"

def create_reminder_task(title: str, reminder_time):
    # 🧠 Ensure reminder_time is a valid datetime object
    if isinstance(reminder_time, str):
        reminder_time = parse(reminder_time)

    if not isinstance(reminder_time, datetime):
        raise ValueError("Invalid reminder_time: must be a datetime object")

    # 🧠 Convert to Unix timestamp
    next_run = int(reminder_time.timestamp())

    # 🧼 Clean up title to avoid double "Reminder:"
    clean_title = title.strip()
    if clean_title.lower().startswith("reminder: reminder:"):
        clean_title = clean_title[len("Reminder: "):]
    elif clean_title.lower().startswith("reminder:"):
        clean_title = clean_title
    else:
        clean_title = f"Reminder: {clean_title}"

    # 🧭 Build task object
    task = {
        "name": clean_title,
        "interval": 0,  # One-time reminder
        "message": f"⏰ Upcoming event: {clean_title} at {reminder_time.strftime('%I:%M %p')}",
        "repeat": False,
        "next_run": next_run
    }

    # 🗂️ Load existing tasks
    tasks = []
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as f:
            try:
                tasks = json.load(f)
            except json.JSONDecodeError:
                tasks = []

    # ➕ Add new task
    tasks.append(task)

    # 💾 Save updated task list
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

    print(f"✅ Reminder task created: {task['name']} at {reminder_time}")
