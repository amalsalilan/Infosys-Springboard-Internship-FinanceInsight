@echo off
echo ============================================================
echo Starting FinSight Application
echo ============================================================
echo.

REM Kill any existing processes on ports 8000-8003 and 8080
echo Cleaning up any existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002" ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8003" ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul

echo.
echo Starting Backend Services...
start "FinSight Backend" cmd /c "uv run python scripts/start_backend.py"

timeout /t 5 /nobreak >nul

echo Starting Frontend...
start "FinSight Frontend" cmd /c "npm run dev"

echo.
echo ============================================================
echo FinSight is starting!
echo ============================================================
echo Backend: http://localhost:8000-8003
echo Frontend: http://localhost:8080
echo.
echo Press any key to open the application in your browser...
pause >nul
start http://localhost:8080
