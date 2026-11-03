@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================
echo  CKA Web Exam Simulator - Install / Start
echo ============================================
echo.

where docker >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker was not found on PATH.
  echo Install Docker Desktop from https://www.docker.com/products/docker-desktop/
  echo then re-run this script.
  exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker is installed but not running.
  echo Start Docker Desktop and wait until it is ready, then re-run this script.
  exit /b 1
)

echo [1/3] Building and starting containers...
docker compose up --build -d
if errorlevel 1 (
  echo [ERROR] docker compose failed.
  exit /b 1
)

echo.
echo [2/3] Waiting for API health...
set /a tries=0
:wait_health
set /a tries+=1
curl.exe -fsS http://localhost:8000/api/health >nul 2>&1
if not errorlevel 1 goto healthy
if %tries% GEQ 60 (
  echo [ERROR] Backend did not become healthy in time.
  echo Check logs with: docker compose logs backend
  exit /b 1
)
timeout /t 2 /nobreak >nul
goto wait_health

:healthy
echo [3/3] Opening UI...
start "" "http://localhost:5173"

echo.
echo Ready.
echo   UI:  http://localhost:5173
echo   API: http://localhost:8000
echo.
echo First "Start Exam" often takes 2-5 minutes while kind provisions the cluster.
echo Stop with:  docker compose down
echo.
endlocal
exit /b 0
