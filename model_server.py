from fastapi import FastAPI
from pydantic import BaseModel
from Shared.llm.phi2_wrapper import get_model_instance, get_model_info
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Phi-2 Model Server")

model = get_model_instance()

class PromptInput(BaseModel):
    prompt: str

@app.post("/generate")
def generate_text(payload: PromptInput):
    logging.info(f"🧠 Received prompt: {payload.prompt}")
    try:
        response = model.query(payload.prompt)
        return {"response": response}
    except Exception as e:
        logging.error(f"❌ Generation failed: {e}")
        return {"error": str(e)}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "model": "phi2",
        **get_model_info()
    }

@app.get("/")
def root():
    return {"message": "Phi-2 Model Server is running"}
