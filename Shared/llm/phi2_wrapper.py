# Shared/llm/phi2_wrapper.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from threading import Thread
from Shared.utils.config import MODEL_PATH, DEVICE, TEMPERATURE, MAX_RESPONSE_TOKENS

class Phi2Model:
    def __init__(self):
        print("🚀 Loading model...")
        dtype = torch.float16 if DEVICE == "cuda" else torch.float32

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, torch_dtype=dtype)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
            ignore_mismatched_sizes=True
        ).to(DEVICE)
        self.model.eval()

        # Optional warm-up
        self.query("Hello")

    def query(self, prompt: str) -> str:
        with torch.no_grad():
            inputs = self.tokenizer(prompt, return_tensors="pt").to(DEVICE)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=MAX_RESPONSE_TOKENS,
                do_sample=True,
                temperature=TEMPERATURE,
                pad_token_id=self.tokenizer.eos_token_id
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

# Singleton instance
_model_instance = Phi2Model()

def query_model(prompt: str) -> str:
    return _model_instance.query(prompt)

def threaded_query_model(prompt: str, callback):
    def worker():
        response = query_model(prompt)
        callback(response)
    Thread(target=worker, daemon=True).start()
