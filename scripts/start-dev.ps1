Write-Host "Starting NLCIL Tender Scrutiny System in Development Mode..." -ForegroundColor Green

# Start backend
Write-Host "Starting Flask backend..."
Start-Process cmd -ArgumentList '/k "cd backend && (if exist .venv\Scripts\python.exe (.venv\Scripts\python.exe run.py) else (python run.py))"' -NoNewWindow:$false

# Start frontend
Write-Host "Starting Vite React frontend..."
Start-Process cmd -ArgumentList '/k "cd frontend && npm run dev"' -NoNewWindow:$false

Write-Host "Both servers started!" -ForegroundColor Green
Write-Host "Backend is available at: http://localhost:5000"
Write-Host "Frontend is available at: http://localhost:5173"
