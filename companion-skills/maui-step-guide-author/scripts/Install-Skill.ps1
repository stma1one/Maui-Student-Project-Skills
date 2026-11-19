param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Project", "Codex", "ClaudeCode")]
    [string] $Target,

    [string] $ProjectPath = "."
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$packageRoot = if (Test-Path (Join-Path $scriptDir "skills\maui-step-guide-author")) { $scriptDir } else { Split-Path -Parent $scriptDir }
$skillSource = Join-Path $packageRoot "skills\maui-step-guide-author"

if (-not (Test-Path $skillSource)) {
    throw "Cannot find skill source: $skillSource"
}

function Install-SkillFiles($Source, $Destination, [bool]$ExcludeEvals) {
    if (Test-Path $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Get-ChildItem -Path $Source | ForEach-Object {
        if ($ExcludeEvals -and $_.Name -eq "evals") {
            return
        }
        Copy-Item -LiteralPath $_.FullName -Destination $Destination -Recurse -Force
    }
}

if ($Target -eq "Project") {
    New-Item -ItemType Directory -Force -Path $ProjectPath | Out-Null
    $resolvedProject = (Resolve-Path $ProjectPath).Path

    $projectAgents = Join-Path $resolvedProject ".agents"
    $projectSkillDest = Join-Path $projectAgents "skills\maui-step-guide-author"
    $projectLearning = Join-Path $resolvedProject "Learning"
    $projectScriptsDest = Join-Path $resolvedProject "Scripts"

    Install-SkillFiles $skillSource $projectSkillDest $true

    New-Item -ItemType Directory -Force -Path (Join-Path $projectLearning "Guides") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $projectLearning "Mockups") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $projectLearning "Images") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $projectLearning "Diagrams") | Out-Null
    New-Item -ItemType Directory -Force -Path $projectScriptsDest | Out-Null

    $toolMap = @{
        "generate_book_pdf.py" = "Generate-Learning-Book-Pdf.py"
        "capture_mockup_blocks.py" = "Capture-Mockup-Blocks.py"
        "validate_learning_book.py" = "Validate-Learning-Book.py"
        "validate_bagrut_compliance.py" = "Validate-Bagrut-Compliance.py"
        "generate_architecture_diagrams.py" = "Generate-Architecture-Diagrams.py"
        "ensure_maui_devflow.py" = "Ensure-Maui-DevFlow.py"
        "ensure_test_project.py" = "Ensure-Test-Project.py"
        "validate_tests.py" = "Validate-Tests.py"
        "requirements-learning-book.txt" = "Learning-Book-Requirements.txt"
    }
    foreach ($entry in $toolMap.GetEnumerator()) {
        $srcTool = Join-Path $skillSource "scripts\$($entry.Key)"
        if (Test-Path $srcTool) {
            Copy-Item -LiteralPath $srcTool -Destination (Join-Path $projectScriptsDest $entry.Value) -Force
        }
    }

    Write-Host "Installed MAUI Step Guide Author skill and Scripts tools into project: $resolvedProject"
    return
}

if ($Target -eq "Codex") {
    $dest = Join-Path $env:USERPROFILE ".codex\skills\maui-step-guide-author"
    Install-SkillFiles $skillSource $dest $false
    Write-Host "Installed Codex skill: $dest"
    return
}

if ($Target -eq "ClaudeCode") {
    $dest = Join-Path $env:USERPROFILE ".claude\skills\maui-step-guide-author"
    Install-SkillFiles $skillSource $dest $false
    Write-Host "Installed Claude Code skill: $dest"
    return
}
