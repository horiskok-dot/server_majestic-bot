@echo off
setlocal
cd /d "%~dp0"

echo.
echo PC Control Windows Agent (ADMIN PROFILE)
echo ========================================

where python >nul 2>nul
if errorlevel 1 (
  echo Python not found. Install Python 3.11+ and enable "Add Python to PATH".
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
  )
)

echo Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Failed to install dependencies.
  pause
  exit /b 1
)

if not exist "C:\Users\horis\AppData\Roaming\PCManager_Agent_admin\agent_config.json" (
  echo ERROR: Config for admin profile not found!
  echo Please make sure the folder C:\Users\horis\AppData\Roaming\PCManager_Agent_admin exists.
  pause
  exit /b 1
)

echo Starting administrative agent...
".venv\Scripts\python.exe" agent.py --profile=admin
echo.
echo Admin Agent stopped. Check C:\Users\horis\AppData\Roaming\PCManager_Agent_admin\logs\agent.log for details.
pause
