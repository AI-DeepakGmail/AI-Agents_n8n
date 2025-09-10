# Server/calendar_api_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from CalendarAgent.calendar import handle_calendar_command

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


@app.get("/health")
def health_check():
    return {"status": "ok"}

# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run("calendar_api_service:app", host="0.0.0.0", port=2703, reload=True)
