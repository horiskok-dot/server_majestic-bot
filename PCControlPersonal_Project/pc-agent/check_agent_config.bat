@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Agent venv not found. Run install_agent_windows.bat first.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" check_agent_config.py
pause
