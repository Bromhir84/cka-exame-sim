# One-line install (Windows):
#   irm https://raw.githubusercontent.com/Bromhir84/cka-exame-sim/main/scripts/install.ps1 | iex
$ErrorActionPreference = "Stop"
# PowerShell 7+ can treat native stderr as errors; git writes progress there.
$prevNative = $null
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $prevNative = $PSNativeCommandUseErrorActionPreference
  $PSNativeCommandUseErrorActionPreference = $false
}

$RepoUrl = if ($env:REPO_URL) { $env:REPO_URL } else { "https://github.com/Bromhir84/cka-exame-sim.git" }
$DirName = if ($env:DIR_NAME) { $env:DIR_NAME } else { "cka-exame-sim" }
$Target = if ($env:TARGET_DIR) { $env:TARGET_DIR } else { Join-Path $HOME $DirName }

Write-Host "==> CKA Exam Simulator installer" -ForegroundColor Cyan

function Test-Cmd($Name) { return [bool](Get-Command $Name -ErrorAction SilentlyContinue) }

# Run a native command; ignore stderr noise; return exit code.
function Invoke-Native {
  param([Parameter(Mandatory)][scriptblock]$Command)
  $prev = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    & $Command 2>&1 | Out-Null
    return $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $prev
  }
}

function Get-NativeText {
  param([Parameter(Mandatory)][scriptblock]$Command)
  $prev = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    $out = & $Command 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    return (($out | Out-String).Trim())
  } finally {
    $ErrorActionPreference = $prev
  }
}

if (-not (Test-Cmd git)) { throw "git is required on PATH" }
if (-not (Test-Cmd docker)) { throw "Docker is required (install Docker Desktop)" }

if ((Invoke-Native { docker info }) -ne 0) {
  throw "Docker is installed but not running. Start Docker Desktop and retry."
}

if (Test-Path (Join-Path $Target ".git")) {
  Write-Host "==> Checking for updates at $Target"
  Push-Location $Target
  try {
    $branch = Get-NativeText { git rev-parse --abbrev-ref HEAD }
    if (-not $branch) { $branch = "main" }
    if ((Invoke-Native { git fetch origin $branch }) -ne 0) {
      Write-Host "    Could not reach origin — continuing with local copy." -ForegroundColor Yellow
    } else {
      $local = Get-NativeText { git rev-parse HEAD }
      $remote = Get-NativeText { git rev-parse "origin/$branch" }
      if ($local -and $remote -and $local -ne $remote) {
        Write-Host "    Update available — pulling origin/$branch..."
        if ((Invoke-Native { git pull --ff-only origin $branch }) -ne 0) {
          Write-Host "    [WARN] git pull failed; continuing with local copy." -ForegroundColor Yellow
        } else {
          Write-Host "    Updated successfully." -ForegroundColor Green
        }
      } else {
        Write-Host "    Already up to date."
      }
    }
  } finally {
    Pop-Location
  }
} else {
  Write-Host "==> Cloning into $Target"
  if ((Invoke-Native { git clone $RepoUrl $Target }) -ne 0) {
    throw "git clone failed"
  }
}

Set-Location $Target
Write-Host "==> Building images (backend, frontend, exam desktop)…"
docker compose build
if ($LASTEXITCODE -ne 0) { throw "docker compose build failed" }
Write-Host "==> Starting stack…"
docker compose up -d
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

Write-Host "==> Waiting for UI + API (http://localhost:5173/api/health)…"
$ready = $false
for ($i = 1; $i -le 90; $i++) {
  try {
    $resp = Invoke-WebRequest -Uri "http://localhost:5173/api/health" -UseBasicParsing -TimeoutSec 3
    if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300) {
      $ready = $true
      break
    }
  } catch {
    # still starting
  }
  Start-Sleep -Seconds 2
}
if (-not $ready) {
  throw "Stack did not become healthy in time. Check: docker compose logs"
}

Write-Host ""
Write-Host "Ready." -ForegroundColor Green
Write-Host "  UI:  http://localhost:5173"
Write-Host "  API: http://localhost:8000"
Write-Host "First Start Exam can take several minutes (kind + networking + optional desktop)."
Write-Host "Stop with:  docker compose down"
Start-Process "http://localhost:5173"

if ($null -ne $prevNative) {
  $PSNativeCommandUseErrorActionPreference = $prevNative
}
