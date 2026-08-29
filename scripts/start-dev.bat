@echo off
echo Starting NLCIL Tender Scrutiny System in Development Mode...

:: Start backend in a new window
echo Starting Flask backend...
start "NLCIL Backend API" cmd /k "cd backend && (if exist .venv\Scripts\python.exe (.venv\Scripts\python.exe run.py) else (python run.py))"

:: Start frontend in a new window
echo Starting Vite React frontend...
start "NLCIL Frontend UI" cmd /k "cd frontend && npm run dev"

echo Both servers started!
echo Backend is available at: http://localhost:5000
echo Frontend is available at: http://localhost:5173
pause
