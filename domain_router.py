#from domains.lights import handle_light_command
#from domains.weather import handle_weather_query
from TaskAgent.tasks import handle_task_command
from CalendarAgent.calendar import handle_calendar_command
from QueryAgent.query import handle_query_command
import re

def normalize(text):
    return re.sub(r"\s+", " ", text.strip().lower())

def route_input(text, callback):
    text = normalize(text)

    # Calendar commands take priority if they include scheduling + reminder
    if any(word in text for word in ["calendar", "schedule", "meeting", "event", "appointment", "book"]):
       return callback(handle_calendar_command(text))
    #elif "light" in text:
       #return callback(handle_light_command(text))
    #elif "weather" in text:
       #return callback(handle_weather_query(text))
    elif text.startswith("task") or text.startswith("remind me to") or text.startswith("add task") or text.startswith("delete task"):
       return callback(handle_task_command(text))
    else:
      return   handle_query_command(text, callback)
