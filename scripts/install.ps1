# One-line install (Windows):
#   irm https://raw.githubusercontent.com/Bromhir84/cka-exame-sim/main/scripts/install.ps1 | iex
$ErrorActionPreference = "Stop"

$RepoUrl = if ($env:REPO_URL) { $env:REPO_URL } else { "https://github.com/Bromhir84/cka-exame-sim.git" }
$DirName = if ($env:DIR_NAME) { $env:DIR_NAME } else { "cka-exame-sim" }
$Target = if ($env:TARGET_DIR) { $env:TARGET_DIR } else { Join-Path $HOME $DirName }

Write-Host "==> CKA Exam Simulator installer" -ForegroundColor Cyan

function Test-Cmd($Name) { return [bool](Get-Command $Name -ErrorAction SilentlyContinue) }

if (-not (Test-Cmd git)) { throw "git is required on PATH" }
if (-not (Test-Cmd docker)) { throw "Docker is required (install Docker Desktop)" }

docker info 1>$null 2>$null
if ($LASTEXITCODE -ne 0) { throw "Docker is installed but not running. Start Docker Desktop and retry." }

if (Test-Path (Join-Path $Target ".git")) {
  Write-Host "==> Checking for updates at $Target"
  Push-Location $Target
  $branch = (git rev-parse --abbrev-ref HEAD).Trim()
  if (-not $branch) { $branch = "main" }
  git fetch origin $branch 2>$null
  if ($LASTEXITCODE -ne 0) {
    Write-Host "    Could not reach origin — continuing with local copy." -ForegroundColor Yellow
  } else {
    $local = (git rev-parse HEAD).Trim()
    $remote = (git rev-parse "origin/$branch").Trim()
    if ($local -ne $remote) {
      Write-Host "    Update available — pulling origin/$branch..."
      git pull --ff-only origin $branch
      if ($LASTEXITCODE -ne 0) {
        Write-Host "    [WARN] git pull failed; continuing with local copy." -ForegroundColor Yellow
      } else {
        Write-Host "    Updated successfully." -ForegroundColor Green
      }
    } else {
      Write-Host "    Already up to date."
    }
  }
  Pop-Location
} else {
  Write-Host "==> Cloning into $Target"
  git clone $RepoUrl $Target
}

Set-Location $Target
Write-Host "==> Building images (backend, frontend, exam desktop)…"
docker compose build
if ($LASTEXITCODE -ne 0) { throw "docker compose build failed" }
Write-Host "==> Starting stack…"
docker compose up -d
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

Write-Host ""
Write-Host "Ready." -ForegroundColor Green
Write-Host "  UI:  http://localhost:5173"
Write-Host "  API: http://localhost:8000"
Write-Host "First Start Exam can take several minutes (kind + networking + optional desktop)."
Write-Host "Stop with:  docker compose down"
Start-Process "http://localhost:5173"
