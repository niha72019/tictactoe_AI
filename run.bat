@echo off
rem Double-click this file to open the project menu.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Setting up the virtual environment for the first time...
    python -m venv .venv
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)
".venv\Scripts\python.exe" main.py %*
pause
