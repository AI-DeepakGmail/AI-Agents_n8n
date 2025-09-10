@echo off
start cmd /k uvicorn model_server:app --host 0.0.0.0 --port 9000
start cmd /k python launch_all_agents.py
