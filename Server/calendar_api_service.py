from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from CalendarAgent.calendar import handle_calendar_command
from CalendarAgent.calendar_suggester import suggest_meeting_time
import uvicorn
import threading

app = FastAPI(title="CalendarAgent API")

class CalendarCommandInput(BaseModel):
    text: str

class SuggestInput(BaseModel):
    description: str

@app.post("/calendar-command")
def api_calendar_command(payload: CalendarCommandInput):
    try:
        result = handle_calendar_command(payload.text.strip())
        return {
            "input": payload.text,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/suggest-meeting")
def api_suggest_meeting(payload: SuggestInput):
    result = {"suggestion": None}
    done = threading.Event()

    def capture(response):
        result["suggestion"] = response
        done.set()

    suggest_meeting_time(payload.description.strip(), capture)
    done.wait(timeout=10)

    if result["suggestion"]:
        return {
            "description": payload.description,
            "suggestion": result["suggestion"].strip()
        }
    else:
        raise HTTPException(status_code=504, detail="LLM did not respond in time")

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("calendar_api_service:app", host="0.0.0.0", port=2703, reload=True)
