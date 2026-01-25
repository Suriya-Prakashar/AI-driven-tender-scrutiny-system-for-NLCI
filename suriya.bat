@echo off
SETLOCAL

REM --- Configuration ---
SET PROJECT_DIR=D:\Project\NLCIL-2\file_merge_app
SET PYTHON_APP_PATH=%PROJECT_DIR%\app.py
SET SERVER_URL=http://127.0.0.1:5000
REM ----------------------

REM Go to project folder
cd /d "%PROJECT_DIR%"

REM Start N8N (minimized)
start "N8N" /min n8n.cmd

REM Start Python app with NO console window
REM If this fails, change pythonw.exe to python.exe
start "Python App" /min pythonw.exe "%PYTHON_APP_PATH%"

REM Wait until the server is actually up (max ~30s)
powershell -Command "for ($i=0; $i -lt 30; $i++) { try { $r = Invoke-WebRequest '%SERVER_URL%' -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Seconds 1 }"

REM Open the UI in browser
start "" "%SERVER_URL%"

ENDLOCAL
