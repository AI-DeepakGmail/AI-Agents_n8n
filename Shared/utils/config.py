# Shared/utils/config.py
# Model settings
#MODEL_PATH = "D:/LLMModels/phi-2"
MODEL_PATH = "G:/LLMModels/phi-2"
DEVICE ="cpu"

# Agent behavior
TEMPERATURE = 0.7
MAX_RESPONSE_TOKENS = 150

# File paths
TASK_FILE = "Shared/data/tasks.json"
#LOG_FILE = "agent_log.json"


# utils/config.py
AGENTS = {
    "calendar": {
        "enabled": True,
        "port": 2703,
        "entry": "Server.calendar_api_service:app"
    },
    "query": {
        "enabled": True,
        "port": 2701,
        "entry": "Server.query_api:app"
    },
    "task": {
        "enabled": True,
        "port": 2702,
        "entry": "Server.task_api:app"
    }
}


