# calendar_suggester.py
from Shared.llm.phi2_wrapper import threaded_query_model
from .outlook_emailer import send_email

def suggest_meeting_time(text, callback):
    prompt = f"Suggest an optimal meeting time for: {text}. Avoid conflicts and prefer working hours."
    threaded_query_model(prompt, callback)


