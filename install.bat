@echo off
setlocal EnableExtensions EnableDelayedExpansion
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

REM --- Always install origin/main. Do not keep an older copy running. ---
where git >nul 2>&1
if errorlevel 1 (
  echo [ERROR] git was not found on PATH.
  echo The installer will not start an older copy without it.
  exit /b 1
)
if not exist ".git" (
  echo [ERROR] This folder is not a git checkout, so it cannot update to origin/main.
  echo Clone https://github.com/Bromhir84/cka-exame-sim and run install.bat there.
  exit /b 1
)

echo [0/3] Updating to origin/main...
git fetch origin main
if errorlevel 1 (
  echo [ERROR] Could not fetch origin/main. Refusing to start an older copy.
  exit /b 1
)
echo        Checking out origin/main. Local changes in this folder are replaced.
git checkout -f -B main origin/main
if errorlevel 1 (
  echo [ERROR] Could not check out origin/main.
  exit /b 1
)
for /f "delims=" %%h in ('git rev-parse HEAD') do set "GIT_SHA=%%h"
echo        Building version !GIT_SHA:~0,7!
echo.

echo [1/3] Rebuilding the UI image, then the API...
docker compose build --no-cache frontend
if errorlevel 1 (
  echo [ERROR] docker compose build frontend failed.
  exit /b 1
)
docker compose build backend
if errorlevel 1 (
  echo [ERROR] docker compose build backend failed.
  exit /b 1
)
echo Starting containers...
docker compose up -d --force-recreate
if errorlevel 1 (
  echo [ERROR] docker compose up failed.
  exit /b 1
)

echo.
echo [2/3] Waiting for UI + API (via http://localhost:5173/api/health)...
set /a tries=0
:wait_health
set /a tries+=1
curl.exe -fsS http://localhost:5173/api/health >nul 2>&1
if not errorlevel 1 goto healthy
if %tries% GEQ 90 (
  echo [ERROR] Stack did not become healthy in time.
  echo Check logs with: docker compose logs
  exit /b 1
)
timeout /t 2 /nobreak >nul
goto wait_health

:healthy
echo Pulling cluster images (reused by every kind cluster)...
docker compose exec -T backend python -m app.preload_images
if errorlevel 1 (
  echo [ERROR] Failed to pull cluster images.
  echo Check logs with: docker compose logs backend
  exit /b 1
)

echo [3/3] Opening UI...
start "" "http://localhost:5173/?v=!GIT_SHA:~0,7!"

echo.
echo Ready ^(build !GIT_SHA:~0,7!^).
echo   UI:  http://localhost:5173
echo   API: http://localhost:8000
echo.
echo Reload the exam page if it was already open.
echo The header should say build !GIT_SHA:~0,7!.
echo.
echo Cluster images are cached. New clusters load them instead of downloading again.
echo The first cluster still takes a few minutes to boot.
echo Stop with:  docker compose down
echo.
endlocal
exit /b 0
