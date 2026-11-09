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
  Write-Host "==> Updating $Target to origin/main"
  Push-Location $Target
  try {
    if ((Invoke-Native { git fetch origin main }) -ne 0) {
      throw "Could not fetch origin/main. Refusing to start an older copy."
    }
    # The install directory is the running app. Local edits must not keep the old UI.
    Write-Host "    Checking out origin/main. Local changes in this folder are replaced."
    if ((Invoke-Native { git checkout -f -B main origin/main }) -ne 0) {
      throw "Could not check out origin/main."
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
$env:GIT_SHA = Get-NativeText { git rev-parse HEAD }
if (-not $env:GIT_SHA) { throw "Could not read the installed commit" }
$short = $env:GIT_SHA.Substring(0, [Math]::Min(7, $env:GIT_SHA.Length))
Write-Host "==> Building version $short"
Write-Host "    Rebuilding the UI image so the exam clock fix is the one that runs."
docker compose build --no-cache frontend
if ($LASTEXITCODE -ne 0) { throw "docker compose build frontend failed" }
docker compose build backend
if ($LASTEXITCODE -ne 0) { throw "docker compose build backend failed" }
Write-Host "==> Starting stack…"
docker compose up -d --force-recreate
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

Write-Host "==> Pulling cluster images (reused by every kind cluster)…"
docker compose exec -T backend python -m app.preload_images
if ($LASTEXITCODE -ne 0) { throw "Failed to pull cluster images. Check: docker compose logs backend" }

Write-Host ""
Write-Host "Ready (build $short)." -ForegroundColor Green
Write-Host "  UI:  http://localhost:5173"
Write-Host "  API: http://localhost:8000"
Write-Host "Reload the exam page if it was already open. The header should say build $short."
Write-Host "Cluster images are cached. New clusters load them instead of downloading again."
Write-Host "The first cluster still takes a few minutes to boot."
Write-Host "Stop with:  docker compose down"
Start-Process "http://localhost:5173/?v=$short"

if ($null -ne $prevNative) {
  $PSNativeCommandUseErrorActionPreference = $prevNative
}
