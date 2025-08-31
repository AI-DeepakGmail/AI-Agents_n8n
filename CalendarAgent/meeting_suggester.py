import re
from dateparser.search import search_dates
from .contact_resolver import resolve_name_interactive
from .outlook_emailer import send_email

def extract_names(text):
    match = re.findall(r"with ([a-zA-Z ,]+)", text.lower())
    if not match:
        return []
    return [name.strip() for name in match[0].split(",")]

def resolve_contacts_interactive(text):
    names = extract_names(text)
    return [resolve_name_interactive(name) for name in names]

def extract_time_slots(text):
    matches = re.findall(
        r"(Monday|Tuesday|Wednesday|Thursday|Friday).*?(\d{1,2} ?[ap]m).*?(\d{1,2} ?[ap]m)",
        text,
        re.IGNORECASE
    )
    slots = []
    for day, start, end in matches:
        parsed_start = search_dates(f"{day} {start}")[0][1]
        parsed_end = search_dates(f"{day} {end}")[0][1]
        slots.append((day.title(), parsed_start, parsed_end))
    return slots

def suggest_meeting(original_text, llm_response):
    emails = resolve_contacts_interactive(original_text)
    if not emails:
        print("⚠️ No known contacts found in text.")
        return

    slots = extract_time_slots(llm_response)
    if not slots:
        print("⚠️ No valid time slots found in LLM response.")
        return

    subject = "Meeting Suggestion"
    body = f"Hi,\n\nLet's meet to discuss:\n{original_text}\n\nAvailable slots:\n"
    body += "\n".join([
        f"{day}: {start.strftime('%I:%M %p')} – {end.strftime('%I:%M %p')}"
        for day, start, end in slots
    ])

    for email in emails:
        send_email(to=email, subject=subject, body=body)
