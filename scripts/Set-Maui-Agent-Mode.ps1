param(
    [ValidateSet("student","code")]
    [string]$Mode = "student",
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot
)

$configPath = Join-Path $ProjectRoot ".agents\MAUI-Agent-Mode.json"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $configPath) | Out-Null

if ($Mode -eq "student") {
    $value = $true
    $label = "MAXIMIZE STUDENT CAPABILITY"
} else {
    $value = $false
    $label = "MAXIMIZE CODE GENERATED"
}

$config = @{
    studentCapabilityMode = $value
    description = @{
        true = "MAXIMIZE STUDENT CAPABILITY: staged planning, concept gates, ownership negotiation, student practice, and verification."
        false = "MAXIMIZE CODE GENERATED: implement complete feature slices efficiently while preserving verification and learning documentation when configured."
    }
} | ConvertTo-Json -Depth 4

$config | Set-Content $configPath -Encoding UTF8

Write-Host "Instructor updated agent mode to: $label in $configPath" -ForegroundColor Green
