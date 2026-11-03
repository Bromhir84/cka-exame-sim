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

REM --- Check for repo updates (best-effort; skip if offline / no git) ---
if exist ".git" (
  where git >nul 2>&1
  if not errorlevel 1 (
    echo [0/3] Checking for updates...
    set "BRANCH=main"
    for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set "BRANCH=%%b"
    git fetch origin "!BRANCH!" >nul 2>&1
    if errorlevel 1 (
      echo       Could not reach origin — continuing with local copy.
    ) else (
      set "LOCAL="
      set "REMOTE="
      for /f "delims=" %%h in ('git rev-parse HEAD 2^>nul') do set "LOCAL=%%h"
      for /f "delims=" %%h in ('git rev-parse "origin/!BRANCH!" 2^>nul') do set "REMOTE=%%h"
      if not "!LOCAL!"=="" if not "!REMOTE!"=="" if /I not "!LOCAL!"=="!REMOTE!" (
        echo       Update available — pulling origin/!BRANCH!...
        git pull --ff-only origin "!BRANCH!"
        if errorlevel 1 (
          echo       [WARN] git pull failed; continuing with local copy.
        ) else (
          echo       Updated successfully.
        )
      ) else (
        echo       Already up to date.
      )
    )
    echo.
  )
)

echo [1/3] Building images (backend, frontend)...
docker compose build
if errorlevel 1 (
  echo [ERROR] docker compose build failed.
  exit /b 1
)
echo Starting containers...
docker compose up -d
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
echo [3/3] Opening UI...
start "" "http://localhost:5173"

echo.
echo Ready.
echo   UI:  http://localhost:5173
echo   API: http://localhost:8000
echo.
echo First "Start Exam" can take several minutes (kind + networking).
echo Stop with:  docker compose down
echo.
endlocal
exit /b 0
