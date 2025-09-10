# QueryAgent/query_api.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from QueryAgent.query import handle_query_command
import time, logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="QueryAgent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryInput(BaseModel):
    question: str

@app.post("/ask")
def ask_question(query: QueryInput):
    logging.info(f"🧠 Received question: {query.question}")
    start = time.time()

    result = {"response": None}
    def capture(response):
        result["response"] = response

    handle_query_command(query.question, callback=capture)

    return {
        "question": query.question,
        "answer": result["response"],
        "response_time_sec": round(time.time() - start, 2)
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "QueryAgent is running"}
