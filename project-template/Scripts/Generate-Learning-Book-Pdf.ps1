# Generate-Learning-Book-Pdf.ps1
# Runs the PDF generator script to compile MAUI-Learning-Book.md and all guides in Learning/Guides/

param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$AppName = "",
    [string]$OutputPdf = "",
    [string]$ValidationReport = "",
    [switch]$SkipValidation
)

$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "Generate-Learning-Book-Pdf.py"
if (-not (Test-Path $scriptPath)) {
    # Fallback to skill script if not found locally
    $scriptPath = Join-Path $ProjectRoot ".agents\skills\maui-step-guide-author\scripts\generate_book_pdf.py"
}

if (-not (Test-Path $scriptPath)) {
    Write-Error "Could not find generate_book_pdf.py script."
    exit 1
}

$argsList = @("--project-root", $ProjectRoot)
if ($AppName) {
    $argsList += @("--app-name", $AppName)
}
if ($OutputPdf) {
    $argsList += @("--output-pdf", $OutputPdf)
}
if ($ValidationReport) {
    $argsList += @("--validation-report", $ValidationReport)
}
if ($SkipValidation) {
    $argsList += "--skip-validation"
}

Write-Host "Running PDF generation via Python..." -ForegroundColor Cyan
$pyExe = $null
foreach ($candidate in @("python", "python3", "py")) {
    foreach ($cmd in @(Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue)) {
        if ($cmd.Source -match '[\\/]Microsoft[\\/]WindowsApps[\\/]') { continue }
        try {
            & $cmd.Source -c "import sys; raise SystemExit(0 if sys.version_info[0] >= 3 else 1)" *> $null
            if ($LASTEXITCODE -eq 0) { $pyExe = $cmd.Source; break }
        } catch {}
    }
    if ($pyExe) { break }
}
if (-not $pyExe) { $pyExe = "python" }
& $pyExe $scriptPath @argsList

if ($LASTEXITCODE -eq 0) {
    Write-Host "PDF compilation completed successfully." -ForegroundColor Green
} else {
    Write-Error "PDF compilation failed with exit code $LASTEXITCODE"
}
