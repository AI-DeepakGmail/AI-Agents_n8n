import dateparser
import re
from datetime import datetime

def extract_datetime_details(text):
    print(f"🔍 Parsing text: {text}")

    # Extract datetime fragment
    dt_fragment = None
    dt_match = re.search(r"(tomorrow|today|on \w+day)?\s*(at\s*\d{1,2}(:\d{2})?\s*(am|pm)?)", text, re.IGNORECASE)
    if dt_match:
        dt_fragment = dt_match.group().strip()
        print(f"🧪 Extracted datetime fragment: '{dt_fragment}'")

    # Parse datetime
    dt = dateparser.parse(
        dt_fragment if dt_fragment else text,
        settings={
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": datetime.now(),
            "RETURN_AS_TIMEZONE_AWARE": False
        }
    )

    if not dt:
        print("❌ Failed to parse datetime")
        dt = dateparser.parse(text)  # Fallback to full text

    else:
        print(f"✅ Parsed datetime: {dt}")

    # Clean title
    title = text
    title = re.sub(r"(schedule|meeting|event|call|remind)\s+", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\b(tomorrow|today|at|on|am|pm)\b", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\d{1,2}(:\d{2})?\s*(am|pm)?", "", title, flags=re.IGNORECASE)
    title = re.sub(r"for \d+ minutes", "", title, flags=re.IGNORECASE)
    title = re.sub(r"in .+?(?:$| for|\.)", "", title, flags=re.IGNORECASE)
    title = title.strip().title()

    # Duration
    duration_match = re.search(r"for (\d+) minutes", text, re.IGNORECASE)
    duration = int(duration_match.group(1)) if duration_match else 30

    # Location
    location_match = re.search(r"in (.+?)(?:$| for|\.)", text, re.IGNORECASE)
    location = location_match.group(1).strip().replace("the ", "") if location_match else "Office"

    # Participants
    participants_match = re.search(r"with ([\w\s,]+?)(?:$| at| on| for| in)", text, re.IGNORECASE)
    participants = []
    if participants_match:
        raw = participants_match.group(1)
        raw = re.sub(r"\b(tomorrow|today)\b", "", raw, flags=re.IGNORECASE)
        participants = re.split(r",| and ", raw)
        participants = [p.strip().title() for p in participants if p.strip()]

    return {
        "datetime": dt,
        "title": title,
        "duration": duration,
        "location": location,
        "participants": participants
    }
