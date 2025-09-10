import torch
import time
import logging
from threading import Thread, Lock
from transformers import AutoTokenizer, AutoModelForCausalLM
from Shared.utils.config import MODEL_PATH, DEVICE, TEMPERATURE, MAX_RESPONSE_TOKENS

# Setup logging
logging.basicConfig(level=logging.INFO)

class Phi2Model:
    def __init__(self):
        logging.info("🚀 Loading Phi-2 model...")
        self.lock = Lock()
        dtype = torch.float16 if DEVICE == "cuda" else torch.float32

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, torch_dtype=dtype)
            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
                ignore_mismatched_sizes=True
            ).to(DEVICE)
            self.model.eval()
        except Exception as e:
            raise RuntimeError(f"❌ Failed to load Phi-2 model from {MODEL_PATH}: {e}")

        # Optional warm-up
        try:
            self.query("Hello")
        except Exception as e:
            logging.warning(f"⚠️ Warm-up query failed: {e}")

    def query(self, prompt: str) -> str:
        with self.lock, torch.no_grad():
            inputs = self.tokenizer(prompt, return_tensors="pt").to(DEVICE)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=MAX_RESPONSE_TOKENS,
                do_sample=True,
                temperature=TEMPERATURE,
                pad_token_id=self.tokenizer.eos_token_id
            )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

# Lazy singleton instance
_model_instance = None

def get_model_instance():
    global _model_instance
    if _model_instance is None:
        _model_instance = Phi2Model()
    return _model_instance

def query_model(prompt: str) -> str:
    start = time.time()
    try:
        response = get_model_instance().query(prompt)
        duration = round(time.time() - start, 2)
        logging.info(f"🧠 Phi-2 responded in {duration}s")
        return response
    except Exception as e:
        logging.error(f"❌ Query failed: {e}")
        return f"Error: {str(e)}"

def threaded_query_model(prompt: str, callback, timeout: float = 10.0):
    def worker():
        try:
            response = query_model(prompt)
            callback(response)
        except Exception as e:
            callback(f"Error: {str(e)}")

    thread = Thread(target=worker, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

def get_model_info():
    return {
        "model_path": MODEL_PATH,
        "device": DEVICE,
        "max_tokens": MAX_RESPONSE_TOKENS,
        "temperature": TEMPERATURE
    }
