@echo off
setlocal
cd /d "%~dp0"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if not exist backend\.env copy .env.example backend\.env
echo.
echo Installed. Edit backend\.env before starting the server.
pause
