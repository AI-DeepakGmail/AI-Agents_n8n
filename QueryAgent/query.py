# QueryAgent/query.py

from Shared.llm.llm_client import threaded_query_model

def handle_query_command(user_input: str, callback=None):
    try:
        user_input = user_input.lower().strip()
        prompt = (
            f"You are a factual assistant. Answer the following question clearly and concisely.\n"
            f"Question: {user_input}\n"
            f"Answer:"
        )
        threaded_query_model(prompt, callback)
    except Exception as e:
        if callback:
            callback(f"⚠️ Error handling query command: {e}")
        else:
            print(f"⚠️ Error: {e}")
