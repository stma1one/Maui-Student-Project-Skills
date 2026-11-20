param(
    [Parameter(Position = 0)]
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [switch]$SkipDotnetRun,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

$ErrorActionPreference = "Stop"
if ($ProjectRoot -and $ProjectRoot.StartsWith("-")) {
    if ($ProjectRoot -match '^(--skip-dotnet-run|-SkipDotnetRun)$') { $SkipDotnetRun = $true }
    $ProjectRoot = (Split-Path -Parent $PSScriptRoot)
}
if (Test-Path -LiteralPath $ProjectRoot) { $ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path }
if ($ProjectRoot.Length -gt 3) { $ProjectRoot = $ProjectRoot.TrimEnd('\', '/') }

$modeFile = Join-Path $ProjectRoot ".agents\MAUI-Agent-Mode.json"
$studentMode = $true
$includeTests = $true
$testManagementMode = "combined"

if (Test-Path -LiteralPath $modeFile) {
    try {
        $modeJson = Get-Content -LiteralPath $modeFile -Raw | ConvertFrom-Json
        if ($null -ne $modeJson.studentCapabilityMode) { $studentMode = [bool]$modeJson.studentCapabilityMode }
        if ($null -ne $modeJson.includeTests) { $includeTests = [bool]$modeJson.includeTests }
        if ($modeJson.testManagementMode) { $testManagementMode = [string]$modeJson.testManagementMode }
    } catch {}
}

if (-not $includeTests) {
    Write-Host "[SKIP] includeTests=false in .agents/MAUI-Agent-Mode.json — unit tests are disabled (testManagementMode ignored)." -ForegroundColor Yellow
    Write-Host "RESULT: PASS (TESTS DISABLED)" -ForegroundColor Green
    exit 0
}

function Find-WorkingPython3 {
    foreach ($candidate in @("python", "python3", "py")) {
        $cmds = @(Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue)
        foreach ($cmd in $cmds) {
            if ($cmd.Source -match '[\\/]Microsoft[\\/]WindowsApps[\\/]') { continue }
            try {
                if ($candidate -eq "py") {
                    & $cmd.Source -3 -c "import sys; raise SystemExit(0 if sys.version_info[0] >= 3 else 1)" *> $null
                    if ($LASTEXITCODE -eq 0) { return ,@($cmd.Source, "-3") }
                } else {
                    & $cmd.Source -c "import sys; raise SystemExit(0 if sys.version_info[0] >= 3 else 1)" *> $null
                    if ($LASTEXITCODE -eq 0) { return ,@($cmd.Source) }
                }
            } catch {}
        }
    }
    $localPaths = @()
    $localPaths += Get-ChildItem -Path "C:\Python3*\python.exe" -ErrorAction SilentlyContinue
    if ($env:LocalAppData) {
        $localPaths += Get-ChildItem -Path (Join-Path $env:LocalAppData "Programs\Python\Python3*\python.exe") -ErrorAction SilentlyContinue
    }
    if ($env:ProgramFiles) {
        $localPaths += Get-ChildItem -Path (Join-Path $env:ProgramFiles "Python3*\python.exe") -ErrorAction SilentlyContinue
    }
    foreach ($exe in ($localPaths | Sort-Object FullName -Descending)) {
        try {
            & $exe.FullName -c "import sys; raise SystemExit(0 if sys.version_info[0] >= 3 else 1)" *> $null
            if ($LASTEXITCODE -eq 0) { return ,@($exe.FullName) }
        } catch {}
    }
    return $null
}

$scriptPath = Join-Path $PSScriptRoot "Validate-Tests.py"
if (-not (Test-Path -LiteralPath $scriptPath)) {
    $scriptPath = Join-Path $ProjectRoot ".agents\skills\maui-step-guide-author\scripts\validate_tests.py"
}

$pythonSpec = @(Find-WorkingPython3 | Where-Object { $null -ne $_ -and $_ -ne "" })
if ($pythonSpec.Count -gt 0 -and (Test-Path -LiteralPath $scriptPath)) {
    $pyExe = [string]$pythonSpec[0]
    $pyArgs = @()
    if ($pythonSpec.Count -gt 1) { $pyArgs += $pythonSpec[1..($pythonSpec.Count - 1)] }
    $pyArgs += @($scriptPath, "--project-root", $ProjectRoot)
    if ($SkipDotnetRun) { $pyArgs += "--skip-dotnet-run" }
    & $pyExe @pyArgs
    exit $LASTEXITCODE
}

# Native PowerShell fallback if Python is unavailable
$effectiveWriter = if (-not $studentMode) { "agent" } else { $testManagementMode }
Write-Host "[INFO] Validating xUnit tests (includeTests=true, testManagementMode=$testManagementMode, effective writer=$effectiveWriter)" -ForegroundColor Cyan

$testCsprojs = Get-ChildItem -Path $ProjectRoot -Recurse -Filter "*.Tests.csproj" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "[\\/](bin|obj|\.git|\.vs|\.agents|project-template)[\\/]" }

if (-not $testCsprojs -or $testCsprojs.Count -eq 0) {
    Write-Host "[FAIL] No *.Tests.csproj found under $ProjectRoot. Run .\Scripts\Ensure-Test-Project.ps1." -ForegroundColor Red
    exit 1
}

$testDoc = Join-Path $ProjectRoot "Learning\Test-Documentation.md"
if (-not (Test-Path -LiteralPath $testDoc) -or ((Get-Item -LiteralPath $testDoc).Length -eq 0)) {
    Write-Host "[FAIL] Missing or empty $testDoc. Document all executed tests in Learning/Test-Documentation.md." -ForegroundColor Red
    exit 1
}

if ($SkipDotnetRun) {
    Write-Host "RESULT: PASS" -ForegroundColor Green
    exit 0
}

$totalPassed = 0
$totalFailed = 0
foreach ($tc in $testCsprojs) {
    $tcText = Get-Content -LiteralPath $tc.FullName -Raw
    if ($tcText -match '<PackageReference\s+[^>]*Include\s*=\s*"xunit"\b') {
        Write-Host "[FAIL] $($tc.Name) references legacy 'xunit' (v2). Must use 'xunit.v3' (latest stable)." -ForegroundColor Red
        exit 1
    }
    $out = & dotnet run --project $tc.FullName 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-Host $out -ForegroundColor Red
        Write-Host "[FAIL] xunit.v3 test execution failed for $($tc.Name)" -ForegroundColor Red
        exit 1
    }
    if ($out -match 'Total:\s*(\d+),\s*Errors:\s*(\d+),\s*Failed:\s*(\d+),\s*Skipped:\s*(\d+)') {
        $tot = [int]$Matches[1]; $err = [int]$Matches[2]; $fail = [int]$Matches[3]; $skip = [int]$Matches[4]
        $totalFailed += ($err + $fail)
        $totalPassed += [Math]::Max(0, $tot - $err - $fail - $skip)
    } elseif ($out -match '(?m)^\s*succeeded:\s*(\d+)') {
        $totalPassed += [int]$Matches[1]
        if ($out -match '(?m)^\s*failed:\s*(\d+)') { $totalFailed += [int]$Matches[1] }
    } elseif ($out -match 'Failed:\s*(\d+),\s*Passed:\s*(\d+)') {
        $totalFailed += [int]$Matches[1]
        $totalPassed += [int]$Matches[2]
    } elseif ($out -match 'Passed:\s*(\d+)') {
        $totalPassed += [int]$Matches[1]
    }
}

if ($totalFailed -gt 0 -or $totalPassed -lt 1) {
    Write-Host "[FAIL] Unit test gate requires Failed == 0 and Passed >= 1 (actual Passed: $totalPassed, Failed: $totalFailed)." -ForegroundColor Red
    exit 1
}

Write-Host "RESULT: PASS (Passed: $totalPassed, Failed: $totalFailed, Effective Writer: $effectiveWriter)" -ForegroundColor Green
exit 0
