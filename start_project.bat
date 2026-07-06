@echo off
REM ============================================================
REM  Material Selection Optimizer - one-click startup
REM  Starts: XAMPP MySQL, Flask backend, frontend HTTP server
REM ============================================================

echo Starting XAMPP MySQL...
start "" "C:\Users\yash dinkar desai\OneDrive\Desktop\Xampp\mysql_start.bat"

REM give MySQL a few seconds to actually come up
timeout /t 5 /nobreak > nul

echo Starting Flask backend...
start "Backend - Flask API" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && set DB_USER=root && set DB_PASSWORD= && python app.py"

REM give Flask a moment to bind to port 5000
timeout /t 3 /nobreak > nul

echo Starting frontend server...
start "Frontend - HTTP Server" cmd /k "cd /d %~dp0frontend && python -m http.server 8000"

timeout /t 2 /nobreak > nul

echo Opening browser...
start http://localhost:8000

echo.
echo All three services launching in separate windows.
echo Close this window any time - the other three stay running.
pause
