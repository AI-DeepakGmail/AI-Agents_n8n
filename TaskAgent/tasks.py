from .task_utils import add_task, update_task, delete_task, list_tasks, clean_message
from Shared.llm.phi2_wrapper import threaded_query_model
import re

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
    return value

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

def extract_task_name(text, command_prefix="add task"):
    time_expr = re.search(r"(in|every)\s+\d+\s*(s|sec|secs|seconds|m|min|mins|minutes|h|hr|hrs|hours)?", text)
    if time_expr:
        return text[:time_expr.start()].replace(command_prefix, "").strip()
    return text.replace(command_prefix, "").strip()

def handle_task_command(text, callback=None):
    try:
        text = text.lower().strip()

        # Natural language fallback
        if "remind me to" in text:
            task_match = re.search(r"remind me to (.+?) (in|every|at) \d+", text)
            name = None
            if task_match:
                name = task_match.group(1).strip()
            else:
                name_match = re.search(r"remind me to (.+)", text)
                if name_match:
                    name = name_match.group(1).strip()

            if name:
                interval = parse_interval(text)
                if interval and interval < 60:
                    interval = None
                time_of_day = parse_time_of_day(text) if not interval else None
                repeat = "every" in text or "daily" in text

                prompt = (
                    f"You are a helpful assistant. "
                    f"Generate a short, encouraging reminder for the task: '{name}'. "
                    f"Make it friendly and motivational."
                )

                def finish(msg):
                    cleaned = clean_message(msg)
                    add_task(name, interval, cleaned, repeat, time_of_day)
                    print(f"\n✅ Task '{name}' added with LLM-generated message:\n💬 {cleaned}\n>> ", end="", flush=True)

                threaded_query_model(prompt, callback or finish)
                return "⏳ Generating reminder message..."

        # ADD TASK
        if text.startswith("add task"):
            name = extract_task_name(text, "add task")
            interval = parse_interval(text)
            if interval and interval < 60:
                interval = None
            time_of_day = parse_time_of_day(text) if not interval else None

            if not name:
                name = input("📝 What should I call this task? ").strip()

            if not interval and not time_of_day:
                interval_input = input("⏱️ How often should I remind you (e.g., 30s, 2min, 1hr or 7am)? ").strip()
                interval = parse_interval(f"in {interval_input}")
                if interval and interval < 60:
                    interval = None
                time_of_day = parse_time_of_day(interval_input) if not interval else None
                if not interval and not time_of_day:
                    return "⚠️ Couldn't understand the interval or time."

            message = input(f"💬 What should I say when reminding '{name}'? (Leave blank to auto-generate) ").strip()
            repeat_input = input("🔁 Should this task repeat? (yes/no): ").strip().lower()
            repeat = repeat_input in ["yes", "y", "true", "repeat"]

            if message:
                add_task(name, interval, message, repeat, time_of_day)
                return f"✅ Task '{name}' added {'every ' + str(interval) + ' seconds' if interval else 'at ' + time_of_day}. Repeat: {repeat}"
            else:
                prompt = f"Generate a friendly reminder for the task: '{name}'"

                def finish_task(msg):
                    cleaned = clean_message(msg)
                    add_task(name, interval, cleaned, repeat, time_of_day)
                    print(f"\n✅ Task '{name}' added with LLM-generated message:\n💬 {cleaned}\n>> ", end="", flush=True)

                threaded_query_model(prompt, callback or finish_task)
                return "⏳ Generating reminder message..."

        # UPDATE TASK
        elif text.startswith("update task"):
            name = extract_task_name(text, "update task")
            interval = parse_interval(text)
            if interval and interval < 60:
                interval = None
            time_of_day = parse_time_of_day(text) if not interval else None

            if not name:
                name = input("📝 Which task do you want to update? ").strip()

            if not interval and not time_of_day:
                interval_input = input("⏱️ New interval or time (e.g., 30s, 2min, 7am): ").strip()
                interval = parse_interval(f"in {interval_input}")
                if interval and interval < 60:
                    interval = None
                time_of_day = parse_time_of_day(interval_input) if not interval else None
                if not interval and not time_of_day:
                    return "⚠️ Couldn't understand the interval or time."

            message = input("💬 New reminder message (Leave blank to keep existing): ").strip()
            message = message if message else None

            update_task(name, interval, message, time_of_day)
            return f"🔄 Task '{name}' updated."

        # DELETE TASK
        elif text.startswith("delete task"):
            name = text.split("delete task")[1].strip()
            if not name:
                name = input("🗑️ Which task do you want to delete? ").strip()
            delete_task(name)
            return f"🗑️ Task '{name}' deleted."

        # LIST TASKS
        elif text.startswith("list tasks"):
            tasks = list_tasks()
            if not tasks:
                return "📭 No tasks scheduled."
            return "\n".join([
                f"• {t['name']} → {'every ' + str(t['interval']) + 's' if t.get('interval') else 'at ' + t.get('time_of_day', '?')} {'(repeats)' if t.get('repeat', True) else '(one-time)'}"
                for t in tasks
            ])

        else:
            return "❓ Use: add task, update task, delete task, list tasks"

    except Exception as e:
        return f"⚠️ Error handling task command: {e}"
