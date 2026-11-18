param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = "Stop"

$csproj = Get-ChildItem $ProjectRoot -Filter "*.csproj" -Recurse -File |
    Where-Object { $_.FullName -notmatch "\\bin\\|\\obj\\|\\Tests\\|\\.Tests\\" } |
    Select-Object -First 1

if (-not $csproj) {
    Write-Host "No MAUI app .csproj found." -ForegroundColor Red
    exit 2
}

$text = Get-Content $csproj.FullName -Raw
$match = [regex]::Match($text, '<TargetFrameworks?>\s*([^<]+)')
$tfm = if ($match.Success) { $match.Groups[1].Value.Trim() } else { "" }

Write-Host "Project: $($csproj.FullName)"
Write-Host "Target framework: $tfm"

if (-not $tfm -or $tfm -notmatch '\bnet(8|9|10|11)\.0') {
    Write-Host "ERROR: TargetFramework '$tfm' is not a supported modern .NET MAUI target (net8.0, net9.0, net10.0, or net11.0)." -ForegroundColor Red
    Write-Host "RESULT: CHECK REQUIRED" -ForegroundColor Yellow
    exit 1
}

if ($tfm -match 'net11\.0') {
    Write-Host "NOTICE: .NET 11 MAUI is preview. Avoid preview-only APIs unless required." -ForegroundColor Yellow
}
else {
    Write-Host "Target framework verified ($tfm)." -ForegroundColor Green
}

$whatNew = "https://learn.microsoft.com/en-us/dotnet/maui/whats-new/?view=net-maui-10.0"
try {
    Invoke-WebRequest -Uri $whatNew -UseBasicParsing -TimeoutSec 5 | Out-Null
    Write-Host "Online Microsoft Learn reference reachable." -ForegroundColor Gray
}
catch {
    Write-Host "OFFLINE NOTICE: Microsoft Learn could not be reached in this network environment; local TFM validation passed." -ForegroundColor Gray
}

Write-Host "RESULT: PASS" -ForegroundColor Green
exit 0
