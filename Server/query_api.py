# Server/query_api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Shared.llm.phi2_wrapper import query_model
import uvicorn
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="QueryAgent API")

# Optional: Enable CORS if calling from frontend or remote n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain if needed
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryInput(BaseModel):
    question: str

@app.post("/ask")
def ask_question(query: QueryInput):
    logging.info(f"🧠 Received question: {query.question}")
    start = time.time()

    prompt = (
        f"You are a factual assistant. Answer the following question clearly and concisely.\n"
        f"Question: {query.question.strip()}\n"
        f"Answer:"
    )
    response = query_model(prompt)
    duration = round(time.time() - start, 2)

    return {
        "question": query.question,
        "answer": response.strip(),
        "response_time_sec": duration
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "QueryAgent is running"}

if __name__ == "__main__":
    uvicorn.run("query_api:app", host="0.0.0.0", port=2701, reload=True)
