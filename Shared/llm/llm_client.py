import requests

def query_model(prompt: str) -> str:
    try:
        response = requests.post("http://localhost:9000/generate", json={"prompt": prompt})
        return response.json().get("response", "No response")
    except Exception as e:
        return f"Error: {str(e)}"

def threaded_query_model(prompt, callback, timeout=100):
    import threading

    result = {"response": None}
    done = threading.Event()

    def worker():
        try:
            response = query_model(prompt)
            result["response"] = response
        except Exception as e:
            result["response"] = f"Error: {str(e)}"
        finally:
            done.set()  # Signal that we're done

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    done.wait(timeout)  # Wait for signal or timeout

    callback(result["response"] if result["response"] else "⚠️ Timeout or empty response")

