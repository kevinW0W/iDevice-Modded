param(
    [Parameter(Mandatory = $true)]
    [string]$InstallRoot
)

$ErrorActionPreference = 'Stop'
$resolvedRoot = [System.IO.Path]::GetFullPath($InstallRoot).TrimEnd('\') + '\'
$processes = Get-CimInstance Win32_Process -ErrorAction Stop |
    Where-Object {
        $_.ExecutablePath -and
        $_.ExecutablePath.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)
    }

foreach ($process in $processes) {
    Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Milliseconds 500
