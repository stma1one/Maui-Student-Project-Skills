param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = "Stop"
if (Test-Path -LiteralPath $ProjectRoot) { $ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path }
if ($ProjectRoot.Length -gt 3) { $ProjectRoot = $ProjectRoot.TrimEnd('\', '/') }

$scriptPath = Join-Path $PSScriptRoot "Generate-Architecture-Diagrams.py"
$pyCmd = $null
foreach ($candidate in @("python", "python3", "py")) {
    foreach ($cmd in @(Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue)) {
        if ($cmd.Source -match '[\\/]Microsoft[\\/]WindowsApps[\\/]') { continue }
        try {
            & $cmd.Source -c "import sys; raise SystemExit(0 if sys.version_info[0] >= 3 else 1)" *> $null
            if ($LASTEXITCODE -eq 0) { $pyCmd = $cmd.Source; break }
        } catch {}
    }
    if ($pyCmd) { break }
}
if (-not $pyCmd) {
    Write-Error "Python 3 is required to run Generate-Architecture-Diagrams.py"
    exit 2
}

& $pyCmd $scriptPath --project-root $ProjectRoot
exit $LASTEXITCODE
