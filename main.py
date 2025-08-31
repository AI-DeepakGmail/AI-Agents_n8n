import threading
from domain_router import route_input
from TaskAgent.task_utils import run_scheduled_tasks
#from server.api import start_api_server

def start_agent():
    print("🤖 AI Agent Ready. Type your query (or type 'exit'):")

    def show_response(response):
        print(f"\n🧠 {response}\n>> ", end="", flush=True)

    while True:
        user_input = input(">> ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print("🔍 Routing input...", flush=True)
        route_input(user_input, show_response)
        print("⏳ Processing...", flush=True)

if __name__ == "__main__":
    threading.Thread(target=run_scheduled_tasks, daemon=True).start()
    #threading.Thread(target=start_api_server, daemon=True).start()
    start_agent()
