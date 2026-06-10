@echo off
setlocal
cd /d "%~dp0"

echo.
echo PC Control Windows Agent
echo ========================

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

if not exist "agent_config.json" (
  copy "agent_config.example.json" "agent_config.json" >nul
  echo.
  echo Created agent_config.json.
  echo Edit access_key in agent_config.json, then run this file again.
  pause
  exit /b 1
)

findstr /C:"\"access_key\": \"CHANGE_ME\"" agent_config.json >nul
if not errorlevel 1 (
  echo.
  echo access_key is still CHANGE_ME.
  echo Open pc-agent\agent_config.json and paste your server access key.
  pause
  exit /b 1
)

for /f "tokens=*" %%P in ('powershell -NoProfile -Command "$p=(Resolve-Path '.venv\\Scripts\\python.exe').Path; $a=(Resolve-Path 'agent.py').Path; @(Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq $p -and $_.CommandLine -like ('*' + $a + '*') }).Count"') do set AGENT_RUNNING=%%P
if "%AGENT_RUNNING%" NEQ "0" (
  echo.
  echo Agent is already running. Close the existing agent first if you want to restart it.
  echo Log file: %CD%\logs\agent.log
  pause
  exit /b 0
)

echo Starting agent...
".venv\Scripts\python.exe" agent.py
echo.
echo Agent stopped. Check logs\agent.log for details.
pause
