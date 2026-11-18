# Agent Instructions - MAUI K12 Baton Workflow Package

This repository is a distributable agent-skill package, not a MAUI app.

## Editing Rules

- Keep `skills/maui-k12-baton-workflow/SKILL.md` portable and tool-agnostic.
- Keep install instructions in `README.md` synchronized with the folder layout.
- Keep `PACKAGE-MANIFEST.md` synchronized with the package contents and version.
- Keep `project-template/AGENTS.md` focused on target MAUI projects.
- Keep theory evidence, applied coding evidence, and routine-eligibility rules consistent across the workflow, references, templates, and install-time defaults.
- Do not add app-specific details from any source project to the reusable package.

## Validation

Before publishing, check:

```text
skills/maui-k12-baton-workflow/SKILL.md
skills/maui-k12-baton-workflow/references/student-capability-gates.md
skills/maui-k12-baton-workflow/references/maui-specialist-guardrails.md
skills/maui-k12-baton-workflow/evals/evals.json
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/SKILL.md
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/
project-template/AGENTS.md
project-template/.agents/MAUI-Agent-Mode.json
project-template/.agents/templates/phase-status-template.md
project-template/Learning/Current-Phase.md
project-template/Learning/Student-Mastery.md
project-template/Scripts/Setup-Skills.ps1
project-template/Scripts/Setup-Skills.sh
scripts/Install-Skill.ps1
scripts/Install-Skill.sh
scripts/Run-Evals.py
AGENTS.md
CLAUDE.md
README.md
PACKAGE-MANIFEST.md
```

Run `python3 scripts/Run-Evals.py` to validate all `evals.json` files, assertion schemas, referenced files, and shared script hashes.
The package should install and upgrade cleanly in both new and existing .NET MAUI student projects.

## Distribution Goal

The package should help coding agents teach students gradually:

```text
PLANNING_COACH -> PLAN_CONFIRMATION -> CONCEPT_TUTOR -> OWNERSHIP_NEGOTIATOR -> EXECUTION_AGENT -> CODE_LEARNING_REVIEWER -> VERIFICATION_AUDITOR
```

Theory readiness unlocks guided practice. Only theory evidence plus student-authored coding evidence can make a concept routine-eligible for agent-owned repetition.

## MAUI DevFlow Runtime Verification & Guardrail Precedence (v1.4.1)

- **TFM-Gated Provisioning & Opt-Out (`Scripts/Ensure-Maui-DevFlow.py` / `.ps1` / `.sh`)**: Installing or updating the skill on a `.NET MAUI` project injects the pinned `Microsoft.Maui.DevFlow.Agent` (`0.1.0-preview.14.26531.2`) under `Condition="'$(Configuration)' == 'Debug'"` into `.csproj` and `#if DEBUG` `builder.AddMauiDevFlowAgent();` into `MauiProgram.cs` **only when the project targets `net10.0` or `net11.0`** (skipping `net9.0` and older targets such as `net9.0-android`). Injection can be opted out with `-SkipDevFlow` / `--skip-devflow` (`--no-devflow`) or removed with `--remove`.
- **Debug-Only Enforcement**: `Scripts/Validate-Maui-ObsoleteApis.ps1/.sh` fails with `[RELEASE LEAK]` if `Microsoft.Maui.DevFlow` is referenced without a strict positive `Debug` condition (blocking `!= 'Debug'`) or if `AddMauiDevFlowAgent()` / `using Microsoft.Maui.DevFlow` appears outside `#if DEBUG` (blocking `#if !DEBUG`), including when Python is absent in `.sh`.
- **Stage 7 (`VERIFICATION_AUDITOR`) Live Evidence (Only When Installed & Working)**: When `MAUI DevFlow` is installed and actively working on the target platform, the agent runs the app, taps the target control by `AutomationId`, verifies live binding values from the visual tree, and captures a real screenshot into `Learning/Images/`. When `MAUI DevFlow` is not installed or not operational on the active target (e.g., Android/Windows targets where Microsoft's DevFlow support is still "In progress"), it does **not** block `Status: COMPLETE`.
- **Student Mode Bug Hand-Off**: In `studentCapabilityMode=true`, the agent must NEVER auto-fix UI or binding bugs discovered via `MAUI DevFlow`; it reports the visual-tree readout and screenshot to the student and sets `Status: BLOCKED` or `WAITING_FOR_STUDENT`.
- **Precedence over External Skills**: `maui-k12-baton-workflow` guardrails strictly override any external `dotnet/maui-labs` (`maui ai init`) skills (Vanilla C# MVVM and baton gates are never bypassed).
- **`SetProperty(ref ...)` Soft-Gate & ViewModel Scoping**: In ViewModels, prefer explicit 3-line setters (`if (_field == value) return; _field = value; OnPropertyChanged();`). If `SetProperty(ref _field, value)` is encountered or proposed before `Learning/Student-Mastery.md` records mastery of `ref`, do NOT fail the build (`Validate-Maui-ObsoleteApis.ps1/.sh` emits a non-blocking `[PEDAGOGICAL WARNING]` and exits `0`). Instead, issue a pedagogical warning to the student, explain the mechanism (`ref` parameter passing and backing field update), and ask the student whether they prefer to keep it or use the explicit 3-line setter. In Custom Views/Controls (`BindableObject`/`ContentView` in `Views/` or `Controls/`), this restriction does not apply.
