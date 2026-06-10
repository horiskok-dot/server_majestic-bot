@echo off
setlocal
cd /d "%~dp0"

echo.
echo Installing PC Control Windows Agent
echo ==================================

where python >nul 2>nul
if errorlevel 1 (
  echo Python not found. Install Python 3.11+ from https://www.python.org/downloads/windows/
  echo Enable "Add Python to PATH" during install.
  pause
  exit /b 1
)

python --version

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency install failed.
  pause
  exit /b 1
)

if not exist "agent_config.json" (
  copy "agent_config.example.json" "agent_config.json" >nul
  echo Created agent_config.json from example.
)

echo.
echo Next step:
echo 1. Open pc-agent\agent_config.json
echo 2. Replace access_key CHANGE_ME with your server access key
echo 3. Run pc-agent\run_agent.bat
echo.
pause
