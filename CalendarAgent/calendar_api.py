#CalendarAgent/calendar_api.py
import win32com.client
from datetime import timedelta, datetime
import pywintypes
import pytz
import pythoncom
# Initialize Outlook
outlook = win32com.client.Dispatch("Outlook.Application")

# Outlook recurrence constants
OL_RECURS_DAILY = 0
OL_RECURS_WEEKLY = 1

def create_event(title, start, duration=30, location="Auto-scheduled", participants=None, recurrence=None):
    pythoncom.CoInitialize()  # Initialize COM in current thread

    try:
        outlook = win32com.client.Dispatch("Outlook.Application")  # Create COM object inside thread
        appt = outlook.CreateItem(1)  # olAppointmentItem

        # Normalize datetime to naive IST
        start_local = normalize_for_outlook(start)

        appt.Subject = title
        appt.Start = start_local.strftime("%Y-%m-%d %H:%M:%S")
        appt.Duration = duration
        appt.Location = location
        appt.ReminderSet = True
        appt.ReminderMinutesBeforeStart = 10

        # ✅ Set correct time zone explicitly
        tz = outlook.TimeZones.Item("India Standard Time")
        appt.StartTimeZone = tz
        appt.EndTimeZone = tz

        # Add participants
        if participants:
            appt.RequiredAttendees = "; ".join(participants)

        # Handle recurrence safely
        if recurrence:
            print(f"🔁 Applying recurrence: {recurrence}")
            pattern = appt.GetRecurrencePattern()

            recurrence_type = recurrence.get("type", OL_RECURS_DAILY)
            pattern.RecurrenceType = recurrence_type
            pattern.Interval = recurrence.get("interval", 1)

            # Set start and end dates FIRST
            pattern_start = pywintypes.Time(start_local)
            pattern_end = pywintypes.Time(datetime.combine(
                start_local.date() + timedelta(days=recurrence.get("duration_days", 30)),
                datetime.min.time()
            ))
            pattern.PatternStartDate = pattern_start
            pattern.PatternEndDate = pattern_end

            # ✅ Only set DayOfWeekMask if recurrence is weekly
            if recurrence_type == OL_RECURS_WEEKLY and "day_mask" in recurrence:
                day_mask = recurrence["day_mask"]
                if isinstance(day_mask, int):
                    print(f"🗓️ Setting DayOfWeekMask: {day_mask}")
                    pattern.DayOfWeekMask = day_mask
                else:
                    raise ValueError(f"Invalid DayOfWeekMask: {day_mask}")

        appt.Save()

        # Log the event
        log_event(title, start_local, participants, recurrence)

        return {
            "entry_id": appt.EntryID,
            "start": start_local
        }

    finally:
        pythoncom.CoUninitialize()  # Clean up COM for the thread
        
def normalize_for_outlook(dt):
    """Ensure datetime is localized to IST and stripped of tzinfo for Outlook."""
    ist = pytz.timezone('Asia/Kolkata')
    if dt.tzinfo is None:
        dt = ist.localize(dt)
    else:
        dt = dt.astimezone(ist)
    return dt.replace(tzinfo=None)

def log_event(title, dt, participants=None, recurrence=None):
    with open("calendar_log.txt", "a") as f:
        f.write(
            f"{datetime.now()} | Scheduled: {title} at {dt} | "
            f"Participants: {participants or 'None'} | "
            f"Recurrence: {recurrence if recurrence else 'None'}\n"
        )
