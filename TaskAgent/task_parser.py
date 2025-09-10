# TaskAgent/task_parser.py

import re
from TaskAgent.task_utils import add_task, clean_message, parse_interval, parse_time_of_day

def extract_task_name(text, command_prefix="add task"):
    time_expr = re.search(r"(in|every|at)\s+\d+", text)
    if time_expr:
        return text[:time_expr.start()].replace(command_prefix, "").strip()
    return text.replace(command_prefix, "").strip()

def extract_remind_me_task(text):
    match = re.search(r"remind me to (.+?)( in | every | at |$)", text)
    if match:
        return match.group(1).strip()
    return None

def handle_task_command(text, context=None, user_id=None):
    text = text.lower().strip()
    context = context or {}

    # Preserve context first
    name = context.get("name")
    interval = context.get("interval")
    time_of_day = context.get("time_of_day")
    repeat = context.get("repeat") if "repeat" in context else None
    message = context.get("message")

    # Only parse from text if missing
    if not name:
        name = (
            extract_remind_me_task(text)
            if text.startswith("remind me to")
            else extract_task_name(text, "add task")
        )

    if not interval and not time_of_day:
        parsed_interval = parse_interval(text)
        if parsed_interval and parsed_interval >= 60:
            interval = parsed_interval
        else:
            time_of_day = parse_time_of_day(text)

    if repeat is None:
        repeat = "every" in text or "daily" in text

    # Only use text as message if it looks like a message
    # Otherwise, treat it as missing and prompt the user
    if not message:
        if "remind me" in text or "say" in text or "message" in text:
            message = text
        else:
            message = None


    # Check for missing fields
    missing = []
    if not name:
        missing.append("task name")
    if not interval and not time_of_day:
        missing.append("time or interval")
    if not message:
        missing.append("reminder message")
    if repeat is None:
        missing.append("repeat flag")

    if missing:
        return {
            "status": "incomplete",
            "missing": missing,
            "prompt": f"Please provide: {', '.join(missing)}",
            "context": {
                "name": name,
                "interval": interval,
                "time_of_day": time_of_day,
                "repeat": repeat,
                "message": message
            },
            "agent": "task"
        }

    # Task is complete — add it
    print(user_id, name, interval, message, repeat, time_of_day)
    add_task(user_id, name, interval, message, repeat, time_of_day)
    return {
        "status": "added",
        "task": {
            "name": name,
            "interval": interval,
            "time_of_day": time_of_day,
            "repeat": repeat,
            "message": message
        }
    }


