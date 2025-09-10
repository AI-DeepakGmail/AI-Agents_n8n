import subprocess
from Shared.utils.config import AGENTS

def launch_agents():
    print("✅ Launching agents...\n")
    for name, cfg in AGENTS.items():
        if not cfg["enabled"]:
            print(f"⏸️ Skipping {name} agent")
            continue
        print(f"🚀 Starting {name} agent on port {cfg['port']}...")
        subprocess.Popen([
            "uvicorn",
            cfg["entry"],
            "--host", "0.0.0.0",
            "--port", str(cfg["port"])
        ])

if __name__ == "__main__":
    launch_agents()
