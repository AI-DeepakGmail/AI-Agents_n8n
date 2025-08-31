from Shared.llm.phi2_wrapper import threaded_query_model

def handle_query_command(user_input, callback=None):
    try:
      user_input = user_input.lower().strip()
      prompt = (
        f"You are a factual assistant. Answer the following question clearly and concisely.\n"
        f"Question: {user_input}\n"
        f"Answer:"
    )
      threaded_query_model(prompt, callback)
      return   
    except Exception as e:
        return f"⚠️ Error handling query command: {e}"
