#CalendarAgent\calendar.py
from .time_parser import extract_datetime_details
from .calendar_api import create_event, log_event
from .reminder import create_reminder_task  
from datetime import timedelta, datetime
from dateutil.parser import parse as parse_date
import re
from .contact_resolver import resolve_name_interactive

# Outlook recurrence constants
OL_RECURS_DAILY = 0
OL_RECURS_WEEKLY = 1

def extract_lead_minutes(text: str, default: int = 15) -> int:
    match = re.search(r"remind me (\d+)\s*minutes? before", text.lower())
    return int(match.group(1)) if match else default

def clean_title(raw_title: str, text: str) -> str:
    cleaned = re.sub(r"remind me \d+\s*minutes? before", "", raw_title, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or " ".join(text.split()[:5]) + "..."

def title_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())

def parse_recurrence_duration(text: str, default_days: int = 30) -> int:
    text = text.lower()

    match_days = re.search(r"for (\d+)\s*days?", text)
    if match_days:
        return int(match_days.group(1))

    match_weeks = re.search(r"for (\d+)\s*weeks?", text)
    if match_weeks:
        return int(match_weeks.group(1)) * 7

    match_until = re.search(r"until ([a-zA-Z0-9 ,]+)", text)
    if match_until:
        try:
            end_date = parse_date(match_until.group(1), fuzzy=True)
            today = datetime.now()
            delta = (end_date - today).days
            return max(delta, 1)
        except Exception:
            pass

    return default_days

def handle_calendar_command(text):
    details = extract_datetime_details(text)
    dt = details.get("datetime")
    if not dt:
        return "🧠 Couldn't parse a valid time. Please try again with a clearer time reference."

    raw_title = details.get("title") or ""
    title = title_case(clean_title(raw_title, text))

    duration = details.get("duration", 30)
    location = details.get("location", "Office")

    ##################################


    raw_participants = details.get("participants", [])
    participants = [resolve_name_interactive(p) for p in raw_participants]
    ####################################

    recurrence = None
    text_lower = text.lower()

    # 🔁 Prioritize explicit daily recurrence
    if "daily" in text_lower or "every day" in text_lower or re.search(r"\bevery\s+(\d+)?\s*day(s)?\b", text_lower):
        recurrence = {
            "type": OL_RECURS_DAILY,
            "interval": 1,
            "duration_days": parse_recurrence_duration(text_lower, default_days=30)
        }

    # 🔁 Fallback to weekly recurrence if weekday mentioned
    elif re.search(r"\bevery (sunday|monday|tuesday|wednesday|thursday|friday|saturday)\b", text_lower):
        WEEKDAY_MASKS = {
            "sunday": 1,
            "monday": 2,
            "tuesday": 4,
            "wednesday": 8,
            "thursday": 16,
            "friday": 32,
            "saturday": 64
        }
        for day, mask in WEEKDAY_MASKS.items():
            if f"every {day}" in text_lower:
                recurrence = {
                    "type": OL_RECURS_WEEKLY,
                    "interval": 1,
                    "day_mask": mask,
                    "duration_days": parse_recurrence_duration(text_lower, default_days=60)
                }
                break

    print(f"📦 Recurrence parsed: {recurrence}")

    event_info = create_event(
        title=title,
        start=dt,
        duration=duration,
        location=location,
        participants=participants,
        recurrence=recurrence
    )

    log_event(title, dt, participants, recurrence)

    lead_minutes = extract_lead_minutes(text)
    reminder_time = event_info["start"] - timedelta(minutes=lead_minutes)
    create_reminder_task(f"Reminder: {title}", reminder_time)

    return f"📅 Scheduled: '{title}' at {dt.strftime('%Y-%m-%d %I:%M %p')} [ID: {event_info['entry_id']}]"


def extract_participant_emails(text: str) -> list:
    matches = re.findall(r"with ([a-zA-Z ,]+)", text.lower())
    if not matches:
        return []

    names = matches[0].split(",")
    return [resolve_name_interactive(name.strip()) for name in names]
