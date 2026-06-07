@echo off
setlocal

set ROOT=%~dp0
set BACKEND=%ROOT%backend
set FRONTEND=%ROOT%frontend
set VENV=%BACKEND%\venv\Scripts

echo.
echo ============================================================
echo  Warehouse Product Verifier — Starting all services
echo ============================================================
echo.

:: Check Redis (Docker)
echo [1/4] Checking Redis...
docker ps --filter name=wms-redis --filter status=running --format "{{.Names}}" | findstr wms-redis >nul 2>&1
if errorlevel 1 (
    echo      Redis not running — starting Docker container...
    docker start wms-redis >nul 2>&1 || docker run -d --name wms-redis -p 6379:6379 -v wms-redis-data:/data redis:7-alpine redis-server --appendonly yes >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo      Redis started.
) else (
    echo      Redis already running. OK
)

:: FastAPI backend
echo [2/4] Starting FastAPI backend on http://localhost:8000 ...
start "WMS — FastAPI Backend" cmd /k "cd /d %BACKEND% && %VENV%\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul

:: Celery worker
echo [3/4] Starting Celery worker...
start "WMS — Celery Worker" cmd /k "cd /d %BACKEND% && %VENV%\celery.exe -A app.celery_app worker --loglevel=info --concurrency=2 --pool=solo"
timeout /t 2 /nobreak >nul

:: React frontend
echo [4/4] Starting React frontend on http://localhost:5173 ...
start "WMS — React Frontend" cmd /k "cd /d %FRONTEND% && npm run dev"

echo.
echo ============================================================
echo  All services started. Open 3 windows were opened.
echo.
echo  App:      http://localhost:5173
echo  API docs: http://localhost:8000/docs
echo  Health:   http://localhost:8000/health
echo.
echo  Login:    admin@warehouse.com / admin123
echo ============================================================
echo.
pause
