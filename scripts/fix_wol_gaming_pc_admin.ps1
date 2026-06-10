param(
    [switch]$NoRestartAdapter
)

$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$reportDir = Join-Path $rootDir "reports"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$reportPath = Join-Path $reportDir "wol_fix_gaming_pc_$stamp.txt"

function Write-Report {
    param([string]$Text)
    $Text | Tee-Object -FilePath $reportPath -Append
}

function Test-Admin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]$identity
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

Write-Report "PC Control Personal - Wake-on-LAN fix report"
Write-Report "Time: $(Get-Date -Format o)"
Write-Report "Computer: $env:COMPUTERNAME"
Write-Report ""

if (-not (Test-Admin)) {
    Write-Report "ERROR: This script must run as Administrator."
    Write-Report "Right click PowerShell -> Run as administrator, then run this script again."
    exit 1
}

$adapter = Get-NetAdapter -Name "Ethernet" -ErrorAction SilentlyContinue
if (-not $adapter) {
    $adapter = Get-NetAdapter | Where-Object { $_.InterfaceDescription -like "*Realtek*GbE*" } | Select-Object -First 1
}

if (-not $adapter) {
    Write-Report "ERROR: Realtek Ethernet adapter not found."
    exit 2
}

Write-Report "Adapter: $($adapter.Name)"
Write-Report "Description: $($adapter.InterfaceDescription)"
Write-Report "MAC: $($adapter.MacAddress)"
Write-Report "LinkSpeed: $($adapter.LinkSpeed)"
Write-Report ""

$classRoot = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
$driverKey = Get-ChildItem $classRoot -ErrorAction SilentlyContinue |
    Where-Object {
        try {
            (Get-ItemProperty $_.PSPath -ErrorAction Stop).DriverDesc -eq $adapter.InterfaceDescription
        } catch {
            $false
        }
    } |
    Select-Object -First 1

if ($driverKey) {
    $backupReg = Join-Path $reportDir "realtek_wol_registry_backup_$stamp.reg"
    $regPath = "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\$($driverKey.PSChildName)"
    & reg.exe export $regPath $backupReg /y | Out-Null
    Write-Report "Registry backup: $backupReg"

    $registryUpdates = @{
        "S5WakeOnLan" = "1"
        "PowerDownPll" = "0"
        "PnPCapabilities" = 0
    }
    foreach ($name in $registryUpdates.Keys) {
        try {
            Set-ItemProperty -Path $driverKey.PSPath -Name $name -Value $registryUpdates[$name] -ErrorAction Stop
            Write-Report "OK registry $name=$($registryUpdates[$name])"
        } catch {
            Write-Report "WARN registry $name failed: $($_.Exception.Message)"
        }
    }
} else {
    Write-Report "WARN: Realtek registry driver key not found."
}

$advancedUpdates = @(
    @{ Keyword = "*WakeOnMagicPacket"; Value = "1" },
    @{ Keyword = "*WakeOnPattern"; Value = "1" },
    @{ Keyword = "*EEE"; Value = "0" },
    @{ Keyword = "AdvancedEEE"; Value = "0" },
    @{ Keyword = "EnableGreenEthernet"; Value = "0" },
    @{ Keyword = "GigaLite"; Value = "0" },
    @{ Keyword = "PowerSavingMode"; Value = "0" },
    @{ Keyword = "WolShutdownLinkSpeed"; Value = "0" }
)

foreach ($item in $advancedUpdates) {
    try {
        Set-NetAdapterAdvancedProperty -Name $adapter.Name -RegistryKeyword $item.Keyword -RegistryValue $item.Value -NoRestart -ErrorAction Stop
        Write-Report "OK advanced $($item.Keyword)=$($item.Value)"
    } catch {
        Write-Report "WARN advanced $($item.Keyword) failed: $($_.Exception.Message)"
    }
}

try {
    powercfg /deviceenablewake "$($adapter.InterfaceDescription)" | Out-Null
    Write-Report "OK powercfg wake enabled for $($adapter.InterfaceDescription)"
} catch {
    Write-Report "WARN powercfg wake failed: $($_.Exception.Message)"
}

if (-not $NoRestartAdapter) {
    try {
        Write-Report "Restarting adapter to apply driver settings..."
        Restart-NetAdapter -Name $adapter.Name -Confirm:$false -ErrorAction Stop
        Start-Sleep -Seconds 4
        Write-Report "OK adapter restarted"
    } catch {
        Write-Report "WARN adapter restart failed: $($_.Exception.Message)"
    }
}

Write-Report ""
Write-Report "Wake armed devices:"
try {
    powercfg /devicequery wake_armed | Tee-Object -FilePath $reportPath -Append
} catch {
    Write-Report "WARN wake_armed query failed: $($_.Exception.Message)"
}

Write-Report ""
Write-Report "Current Realtek WOL advanced properties:"
try {
    Get-NetAdapterAdvancedProperty -Name $adapter.Name |
        Where-Object { $_.RegistryKeyword -match "Wake|EEE|Green|GigaLite|PowerSaving|WolShutdown" } |
        Select-Object DisplayName, DisplayValue, RegistryKeyword, RegistryValue |
        Format-Table -AutoSize |
        Out-String |
        Tee-Object -FilePath $reportPath -Append
} catch {
    Write-Report "WARN advanced query failed: $($_.Exception.Message)"
}

Write-Report ""
Write-Report "Done. If Wake-on-LAN still fails from full shutdown, enable Wake on LAN / PCI-E wake and disable ErP in BIOS."
Write-Output $reportPath
