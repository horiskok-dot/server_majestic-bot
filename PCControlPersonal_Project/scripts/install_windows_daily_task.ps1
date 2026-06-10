param(
    [string]$TaskName = "PCManager Codex Daily Server Check",
    [string]$RunAt = "10:00"
)

$ErrorActionPreference = "Stop"

$ScriptPath = Join-Path $PSScriptRoot "codex_daily_server_check.ps1"
if (-not (Test-Path $ScriptPath)) {
    throw "Check script not found: $ScriptPath"
}

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ReportsDir = Join-Path $ProjectRoot "reports"
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null

$PowerShellExe = (Get-Command powershell.exe).Source
$Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

$Action = New-ScheduledTaskAction -Execute $PowerShellExe -Argument $Arguments -WorkingDirectory $ProjectRoot
$Trigger = New-ScheduledTaskTrigger -Daily -At $RunAt
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Daily safe SSH health check for PC Manager Ubuntu server. Does not store SSH password." `
    -Force | Out-Null

Write-Host "Task installed: $TaskName"
Write-Host "Schedule: daily at $RunAt"
Write-Host "Script: $ScriptPath"
Write-Host "Reports: $ReportsDir"
Write-Host ""
Write-Host "Important: the scheduled task is non-interactive. Configure SSH key auth, because passwords are not stored."
