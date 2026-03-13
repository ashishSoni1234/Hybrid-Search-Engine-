$ErrorActionPreference = "Stop"

Write-Host "==========================================="
Write-Host " Stopping Hybrid Knowledge Search...       "
Write-Host "==========================================="

$servicesStopped = $false

# Find processes that match our services
$processes = Get-CimInstance Win32_Process | Where-Object { 
    $_.CommandLine -match "uvicorn backend.api.main:app" -or 
    $_.CommandLine -match "streamlit run frontend" 
}

if ($processes) {
    foreach ($proc in $processes) {
        try {
            Stop-Process -Id $proc.ProcessId -Force
            Write-Host "Stopped process ID: $($proc.ProcessId)"
            $servicesStopped = $true
        }
        catch {
            Write-Host "Failed to stop process ID: $($proc.ProcessId)"
        }
    }
}

if (-Not $servicesStopped) {
    Write-Host "No running services found."
}
else {
    Write-Host "==========================================="
    Write-Host " Services stopped cleanly!                 "
    Write-Host "==========================================="
}
