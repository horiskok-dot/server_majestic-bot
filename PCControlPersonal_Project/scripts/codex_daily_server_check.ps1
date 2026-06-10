param(
    [string]$HostName = "192.168.0.194",
    [string]$UserName = "pc",
    [string]$ProjectPath = "/home/pc/PCControlPersonal_Project",
    [switch]$Interactive
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ReportsDir = Join-Path $ProjectRoot "reports"
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null

$DateStamp = Get-Date -Format "yyyy-MM-dd"
$TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$ReportPath = Join-Path $ReportsDir "server_check_$DateStamp.txt"

function Mask-Secrets {
    param([string]$Text)
    $masked = $Text
    $masked = $masked -replace '\b\d{8,12}:[A-Za-z0-9_-]{20,}\b', '[MASKED_TELEGRAM_TOKEN]'
    $masked = $masked -replace '(?im)^(TELEGRAM_BOT_TOKEN|SERVER_ACCESS_KEY|ADMIN_TOKEN|JWT_SECRET|AGENT_BOOTSTRAP_TOKEN)\s*=\s*.+$', '$1=[MASKED]'
    $masked = $masked -replace '(?i)(Bearer|X-Server-Access-Key:|X-PCManager-Key:)\s+[A-Za-z0-9._~+/=-]+', '$1 [MASKED]'
    return $masked
}

function Get-Section {
    param([string]$Text, [string]$Name)
    $pattern = "(?ms)^__SECTION__:$([regex]::Escape($Name))\r?\n(.*?)(?=^__SECTION__:|\z)"
    $match = [regex]::Match($Text, $pattern)
    if ($match.Success) { return $match.Groups[1].Value.Trim() }
    return ""
}

function Add-Suggestion {
    param([System.Collections.Generic.List[string]]$List, [string]$Text)
    if (-not $List.Contains($Text)) { [void]$List.Add($Text) }
}

$RemoteScript = @"
set +e
cd "$ProjectPath" 2>/dev/null

echo "__SECTION__:HOSTNAME_IP"
hostname -I 2>/dev/null

echo "__SECTION__:UPTIME"
uptime 2>/dev/null

echo "__SECTION__:DF"
df -h 2>/dev/null

echo "__SECTION__:DF_ROOT_PERCENT"
df -P / 2>/dev/null | awk 'NR==2 {print $5}'

echo "__SECTION__:FREE"
free -h 2>/dev/null

echo "__SECTION__:RAM_PERCENT"
free 2>/dev/null | awk '/Mem:/ { if (`$2 > 0) printf "%.0f", `$3/`$2*100; }'

echo "__SECTION__:SERVER_ACTIVE"
systemctl is-active pcmanager-server 2>/dev/null

echo "__SECTION__:BOT_ACTIVE"
systemctl is-active pcmanager-bot 2>/dev/null

echo "__SECTION__:PING"
curl -s --max-time 10 http://127.0.0.1:8765/api/ping 2>/dev/null

echo "__SECTION__:SERVER_LOG"
journalctl -u pcmanager-server -n 80 --no-pager 2>/dev/null

echo "__SECTION__:BOT_LOG"
journalctl -u pcmanager-bot -n 80 --no-pager 2>/dev/null
"@

$sshTarget = "$UserName@$HostName"
$sshArgs = @()
if (-not $Interactive) {
    $sshArgs += @("-o", "BatchMode=yes", "-o", "ConnectTimeout=12")
} else {
    $sshArgs += @("-o", "ConnectTimeout=12")
}
$sshArgs += @($sshTarget, "bash -s")

$rawOutput = ""
$sshExitCode = 0
try {
    $rawOutput = $RemoteScript | & ssh @sshArgs 2>&1 | Out-String
    $sshExitCode = $LASTEXITCODE
} catch {
    $rawOutput = $_ | Out-String
    $sshExitCode = 1
}

$safeOutput = Mask-Secrets $rawOutput

$serverActive = Get-Section $safeOutput "SERVER_ACTIVE"
$botActive = Get-Section $safeOutput "BOT_ACTIVE"
$ping = Get-Section $safeOutput "PING"
$dfRootPercentRaw = (Get-Section $safeOutput "DF_ROOT_PERCENT").Trim().TrimEnd("%")
$ramPercentRaw = (Get-Section $safeOutput "RAM_PERCENT").Trim()
$serverLog = Get-Section $safeOutput "SERVER_LOG"
$botLog = Get-Section $safeOutput "BOT_LOG"

$diskPercent = 0
[void][int]::TryParse($dfRootPercentRaw, [ref]$diskPercent)
$ramPercent = 0
[void][int]::TryParse($ramPercentRaw, [ref]$ramPercent)

$logText = "$serverLog`n$botLog"
$problemMatches = [regex]::Matches($logText, '(?i)\b(ERROR|WARNING|Traceback|Exception|failed|disabled|not configured)\b')
$problemCount = $problemMatches.Count

$suggestions = [System.Collections.Generic.List[string]]::new()

$serverStatus = "OK"
if ($sshExitCode -ne 0 -or $serverActive -notmatch '^active$') {
    $serverStatus = "ERROR"
    Add-Suggestion $suggestions "Check SSH access and pcmanager-server: systemctl status pcmanager-server"
}

$botStatus = "OK"
if ($botActive -notmatch '^active$') {
    $botStatus = "ERROR"
    Add-Suggestion $suggestions "Check Telegram bot: systemctl status pcmanager-bot and journalctl -u pcmanager-bot -n 100"
}

$apiStatus = "OK"
if ($ping -notmatch '"ok"\s*:\s*true') {
    $apiStatus = "ERROR"
    Add-Suggestion $suggestions "API does not answer /api/ping. Check pcmanager-server and port 8765."
}

$diskStatus = "OK"
if ($diskPercent -ge 90) {
    $diskStatus = "ERROR"
    Add-Suggestion $suggestions "Disk is almost full. Check /var/lib/pcmanager/storage and old backups."
} elseif ($diskPercent -ge 80) {
    $diskStatus = "WARNING"
    Add-Suggestion $suggestions "Disk usage is high. Clean old logs/backups soon."
}

$ramStatus = "OK"
if ($ramPercent -ge 90) {
    $ramStatus = "ERROR"
    Add-Suggestion $suggestions "High RAM usage. Check processes: ps aux --sort=-%mem | head"
} elseif ($ramPercent -ge 80) {
    $ramStatus = "WARNING"
    Add-Suggestion $suggestions "RAM usage is high. Watch it."
}

if ($problemCount -gt 0) {
    Add-Suggestion $suggestions "Logs contain warnings/errors. See LOG MATCHES below."
}
if ($sshExitCode -ne 0) {
    Add-Suggestion $suggestions "Configure an SSH key for the daily task. Password is intentionally not stored."
}
if ($suggestions.Count -eq 0) {
    Add-Suggestion $suggestions "No urgent issues. Server looks normal."
}

$overall = "OK"
if (@($serverStatus, $apiStatus, $botStatus, $diskStatus, $ramStatus) -contains "ERROR") {
    $overall = "ERROR"
} elseif (@($serverStatus, $apiStatus, $botStatus, $diskStatus, $ramStatus) -contains "WARNING" -or $problemCount -gt 0) {
    $overall = "WARNING"
}

$logMatches = [regex]::Matches($logText, '(?im)^.*\b(ERROR|WARNING|Traceback|Exception|failed|disabled|not configured)\b.*$') |
    Select-Object -First 60 |
    ForEach-Object { $_.Value }

$diskDisplay = "$diskPercent`%"
$ramDisplay = "$ramPercent`%"
$suggestionsText = ($suggestions | ForEach-Object { "- $_" }) -join [Environment]::NewLine
$hostnameText = Get-Section $safeOutput "HOSTNAME_IP"
$uptimeText = Get-Section $safeOutput "UPTIME"
$dfText = Get-Section $safeOutput "DF"
$freeText = Get-Section $safeOutput "FREE"
$logMatchesText = ($logMatches | Out-String).Trim()

$reportLines = @(
    "PC Manager Daily Server Check",
    "Generated: $TimeStamp",
    "Target: $UserName@$HostName",
    "Project: $ProjectPath",
    "",
    "SUMMARY",
    "OVERALL: $overall",
    "SERVER: $serverStatus",
    "API: $apiStatus",
    "BOT: $botStatus",
    "DISK: $diskStatus ($diskDisplay)",
    "RAM: $ramStatus ($ramDisplay)",
    "LOG ERRORS: $problemCount",
    "",
    "SUGGESTIONS",
    $suggestionsText,
    "",
    "REMOTE STATUS",
    "SSH_EXIT_CODE: $sshExitCode",
    "",
    "HOSTNAME -I",
    $hostnameText,
    "",
    "UPTIME",
    $uptimeText,
    "",
    "DF -H",
    $dfText,
    "",
    "FREE -H",
    $freeText,
    "",
    "API PING",
    $ping,
    "",
    "LOG MATCHES",
    $logMatchesText,
    "",
    "SERVER LOG LAST 80",
    $serverLog,
    "",
    "BOT LOG LAST 80",
    $botLog
)
$report = $reportLines -join [Environment]::NewLine

$report = Mask-Secrets $report
$report | Set-Content -Path $ReportPath -Encoding UTF8

Write-Host "Report saved: $ReportPath"
Write-Host "OVERALL: $overall"
Write-Host "SERVER: $serverStatus | API: $apiStatus | BOT: $botStatus | DISK: $diskStatus | RAM: $ramStatus | LOG ERRORS: $problemCount"

if ($overall -eq "ERROR") { exit 2 }
if ($overall -eq "WARNING") { exit 1 }
exit 0
