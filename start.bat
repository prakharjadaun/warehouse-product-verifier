@echo off
setlocal

set ROOT=%~dp0
set BACKEND=%ROOT%backend
set FRONTEND=%ROOT%frontend

echo.
echo ============================================================
echo  Warehouse Product Verifier -- Starting all services
echo ============================================================
echo.

:: Check Redis
echo [1/4] Checking Redis...
docker ps --filter name=wms-redis --filter status=running --format "{{.Names}}" | findstr wms-redis >nul 2>&1
if errorlevel 1 (
    echo      Starting Redis container...
    docker start wms-redis >nul 2>&1 || docker run -d --name wms-redis -p 6379:6379 -v wms-redis-data:/data redis:7-alpine redis-server --appendonly yes >nul 2>&1
    timeout /t 2 /nobreak >nul
) else (
    echo      Redis OK
)

:: Write helper scripts so spaces in paths don't break cmd /k
echo @echo off > "%TEMP%\wms_api.bat"
echo cd /d "%BACKEND%" >> "%TEMP%\wms_api.bat"
echo call venv\Scripts\activate >> "%TEMP%\wms_api.bat"
echo uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload >> "%TEMP%\wms_api.bat"

echo @echo off > "%TEMP%\wms_worker.bat"
echo cd /d "%BACKEND%" >> "%TEMP%\wms_worker.bat"
echo call venv\Scripts\activate >> "%TEMP%\wms_worker.bat"
echo celery -A app.celery_app worker --loglevel=info --concurrency=2 --pool=solo >> "%TEMP%\wms_worker.bat"

echo @echo off > "%TEMP%\wms_frontend.bat"
echo cd /d "%FRONTEND%" >> "%TEMP%\wms_frontend.bat"
echo npm run dev >> "%TEMP%\wms_frontend.bat"

:: Launch each in its own window
echo [2/4] Starting FastAPI backend on http://localhost:8000 ...
start "WMS Backend" cmd /k "%TEMP%\wms_api.bat"
timeout /t 4 /nobreak >nul

echo [3/4] Starting Celery worker...
start "WMS Celery Worker" cmd /k "%TEMP%\wms_worker.bat"
timeout /t 2 /nobreak >nul

echo [4/4] Starting React frontend on http://localhost:5173 ...
start "WMS Frontend" cmd /k "%TEMP%\wms_frontend.bat"

echo.
echo ============================================================
echo  Services started in 3 separate windows.
echo.
echo  App:      http://localhost:5173
echo  API docs: http://localhost:8000/docs
echo  Health:   http://localhost:8000/health
echo.
echo  Login:    admin@warehouse.com / admin123
echo ============================================================
echo.
pause
