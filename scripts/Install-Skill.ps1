param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Project", "Codex", "ClaudeCode")]
    [string] $Target,

    [string] $ProjectPath = ".",

    [switch] $Upgrade,

    [switch] $InstallLearningBookDependencies,

    [Alias("NoDevFlow")]
    [switch] $SkipDevFlow,

    [Alias("NoCli", "SkipDevFlowCli")]
    [switch] $SkipCli
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$packageRoot = Split-Path -Parent $scriptDir
$skillSource = Join-Path $packageRoot "skills\maui-k12-baton-workflow"
$templateRoot = Join-Path $packageRoot "project-template"
$companionSource = Join-Path $packageRoot "companion-skills\maui-step-guide-author\skills\maui-step-guide-author"

if (-not (Test-Path $skillSource)) {
    throw "Cannot find skill source: $skillSource"
}

function Replace-DirectoryClean($Source, $Destination, [bool]$ExcludeEvals = $false) {
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

function Copy-FileIfMissing($Source, $Destination) {
    if (Test-Path $Destination) {
        Write-Host "Preserved existing file: $Destination"
        return
    }

    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    Copy-Item -LiteralPath $Source -Destination $Destination
    Write-Host "Created: $Destination"
}

function Install-OrUpgradeAgentsMd($Source, $Destination, [bool]$IsUpgrade) {
    if (-not (Test-Path $Destination)) {
        Copy-Item -LiteralPath $Source -Destination $Destination
        Write-Host "Created: $Destination"
        return
    }

    $srcHash = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash
    $dstHash = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash
    if ($srcHash -eq $dstHash) {
        Write-Host "AGENTS.md is already up to date."
        return
    }

    $newPath = "$Destination.new"
    Copy-Item -LiteralPath $Source -Destination $newPath -Force
    Write-Host "NOTICE: Existing AGENTS.md differs from package template. Wrote updated template to: $newPath" -ForegroundColor Yellow
}

function Sync-ProjectScripts($TemplateScriptsDir, $CompanionScriptsDir, $DestinationDir, [bool]$IsUpgrade) {
    New-Item -ItemType Directory -Force -Path $DestinationDir | Out-Null

    Get-ChildItem -Path $TemplateScriptsDir -File | ForEach-Object {
        $destFile = Join-Path $DestinationDir $_.Name
        if (-not (Test-Path $destFile)) {
            Copy-Item -LiteralPath $_.FullName -Destination $destFile
            Write-Host "Installed script: $destFile"
        }
        elseif ($IsUpgrade) {
            Copy-Item -LiteralPath $_.FullName -Destination $destFile -Force
            Write-Host "Upgraded script: $destFile"
        }
        else {
            $srcHash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
            $dstHash = (Get-FileHash -LiteralPath $destFile -Algorithm SHA256).Hash
            if ($srcHash -ne $dstHash) {
                Write-Host "NOTICE: Script '$($_.Name)' differs from package version. Re-run with -Upgrade to overwrite." -ForegroundColor Yellow
            }
        }
    }

    # Ensure canonical Python tools from companion skill are synced when upgrading or missing
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
        $srcTool = Join-Path $CompanionScriptsDir $entry.Key
        $dstTool = Join-Path $DestinationDir $entry.Value
        if (Test-Path $srcTool) {
            if ($IsUpgrade -or -not (Test-Path $dstTool)) {
                Copy-Item -LiteralPath $srcTool -Destination $dstTool -Force
            }
        }
    }
}

function Copy-CompanionSkill($Destination, [bool]$ExcludeEvals = $false) {
    if (Test-Path $companionSource) {
        Replace-DirectoryClean $companionSource $Destination $ExcludeEvals
        Write-Host "Installed companion skill: maui-step-guide-author"
    }
}

if ($Target -eq "Project") {
    New-Item -ItemType Directory -Force -Path $ProjectPath | Out-Null
    $resolvedProject = (Resolve-Path $ProjectPath).Path

    Install-OrUpgradeAgentsMd (Join-Path $templateRoot "AGENTS.md") (Join-Path $resolvedProject "AGENTS.md") $Upgrade.IsPresent

    $projectAgents = Join-Path $resolvedProject ".agents"
    $projectSkillDest = Join-Path $projectAgents "skills\maui-k12-baton-workflow"
    $projectTemplateDest = Join-Path $projectAgents "templates"
    $projectLearningDest = Join-Path $resolvedProject "Learning"
    $projectScriptsDest = Join-Path $resolvedProject "Scripts"

    Replace-DirectoryClean $skillSource $projectSkillDest $true
    Replace-DirectoryClean (Join-Path $templateRoot ".agents\templates") $projectTemplateDest
    Copy-CompanionSkill (Join-Path $projectAgents "skills\maui-step-guide-author") $true

    Sync-ProjectScripts (Join-Path $templateRoot "Scripts") (Join-Path $companionSource "scripts") $projectScriptsDest $Upgrade.IsPresent

    New-Item -ItemType Directory -Force -Path $projectAgents | Out-Null
    Copy-FileIfMissing (Join-Path $templateRoot ".agents\MAUI-Agent-Mode.json") (Join-Path $projectAgents "MAUI-Agent-Mode.json")

    foreach ($subDir in @("Learning", "Learning\Guides", "Learning\Mockups", "Learning\Images", "Learning\Diagrams")) {
        New-Item -ItemType Directory -Force -Path (Join-Path $resolvedProject $subDir) | Out-Null
    }
    Copy-FileIfMissing (Join-Path $templateRoot "Learning\Current-Phase.md") (Join-Path $projectLearningDest "Current-Phase.md")
    Copy-FileIfMissing (Join-Path $templateRoot "Learning\Student-Mastery.md") (Join-Path $projectLearningDest "Student-Mastery.md")
    Copy-FileIfMissing (Join-Path $templateRoot "Learning\MAUI-Learning-Book.md") (Join-Path $projectLearningDest "MAUI-Learning-Book.md")
    Copy-FileIfMissing (Join-Path $templateRoot "Learning\Bagrut-Compliance.md") (Join-Path $projectLearningDest "Bagrut-Compliance.md")
    Copy-FileIfMissing (Join-Path $templateRoot "Learning\AI-And-External-Code-Attribution.md") (Join-Path $projectLearningDest "AI-And-External-Code-Attribution.md")
    Copy-FileIfMissing (Join-Path $templateRoot "Learning\Test-Documentation.md") (Join-Path $projectLearningDest "Test-Documentation.md")

    $ensureTests = Join-Path $projectScriptsDest "Ensure-Test-Project.ps1"
    if (Test-Path $ensureTests) {
        & $ensureTests -ProjectRoot $resolvedProject
    }

    $learningBookSetup = Join-Path $projectScriptsDest "Setup-Learning-Book.ps1"
    if (Test-Path $learningBookSetup) {
        $setupArguments = @{ ProjectRoot = $resolvedProject }
        if ($InstallLearningBookDependencies) {
            $setupArguments.InstallMissing = $true
        }

        & $learningBookSetup @setupArguments
    }

    $ensureDevFlow = Join-Path $projectScriptsDest "Ensure-Maui-DevFlow.ps1"
    if ($SkipDevFlow) {
        Write-Host "[SKIP] MAUI DevFlow automatic injection skipped (-SkipDevFlow)." -ForegroundColor Yellow
    }
    elseif (Test-Path $ensureDevFlow) {
        $devFlowArgs = @{ ProjectRoot = $resolvedProject }
        if ($Upgrade) {
            $devFlowArgs.Upgrade = $true
        }
        if ($SkipCli) {
            $devFlowArgs.SkipCli = $true
        }
        & $ensureDevFlow @devFlowArgs
    }

    Write-Host "Installed MAUI K12 Baton Workflow into project: $resolvedProject" -ForegroundColor Green
    return
}

if ($Target -eq "Codex") {
    $dest = Join-Path $env:USERPROFILE ".codex\skills\maui-k12-baton-workflow"
    Replace-DirectoryClean $skillSource $dest
    Copy-CompanionSkill (Join-Path $env:USERPROFILE ".codex\skills\maui-step-guide-author")
    Write-Host "Installed Codex skill: $dest"
    return
}

if ($Target -eq "ClaudeCode") {
    $dest = Join-Path $env:USERPROFILE ".claude\skills\maui-k12-baton-workflow"
    Replace-DirectoryClean $skillSource $dest
    Copy-CompanionSkill (Join-Path $env:USERPROFILE ".claude\skills\maui-step-guide-author")
    Write-Host "Installed Claude Code skill: $dest"
    Write-Host "Also copy CLAUDE.md or project-template\AGENTS.md into the target project root."
    return
}
