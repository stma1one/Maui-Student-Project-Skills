param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Project", "Codex", "ClaudeCode")]
    [string] $Target,

    [string] $ProjectPath = "."
)
& (Join-Path $PSScriptRoot "scripts\Install-Skill.ps1") -Target $Target -ProjectPath $ProjectPath
