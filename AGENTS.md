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

- **Two-Layer TFM-Gated Provisioning & Opt-Out (`Scripts/Ensure-Maui-DevFlow.py` / `.ps1` / `.sh`)**: Installing or updating the skill on a `.NET MAUI` project provisions two layers when the project targets `net10.0` or `net11.0` (skipping `net9.0` and older targets such as `net9.0-android`): (1) Project layer — injects pinned `Microsoft.Maui.DevFlow.Agent` (`0.1.0-preview.14.26531.2`) under `Condition="'$(Configuration)' == 'Debug'"` into `.csproj` and `#if DEBUG` `builder.AddMauiDevFlowAgent();` into `MauiProgram.cs`; and (2) Machine layer — installs or updates the global `.NET MAUI DevFlow CLI` (`dotnet tool install -g Microsoft.Maui.Cli --prerelease`). Opt out of all DevFlow provisioning with `-SkipDevFlow` / `--skip-devflow` (`--no-devflow`), skip global CLI installation with `-SkipCli` / `--skip-cli` when working without global permissions, or remove project injection with `--remove`.
- **Debug-Only Enforcement**: `Scripts/Validate-Maui-ObsoleteApis.ps1/.sh` fails with `[RELEASE LEAK]` if `Microsoft.Maui.DevFlow` is referenced without a strict positive `Debug` condition (blocking `!= 'Debug'`) or if `AddMauiDevFlowAgent()` / `using Microsoft.Maui.DevFlow` appears outside `#if DEBUG` (blocking `#if !DEBUG`), including when Python is absent in `.sh`.
- **Stage 7 (`VERIFICATION_AUDITOR`) Mandatory Visual & PDF Blocking Gate**: It is strictly forbidden to declare `Status: COMPLETE` until one of the two visual pipelines is completed for every screen AND the PDF learning book is compiled (`Learning/MAUI-Learning-Book.pdf` + `Learning/MAUI-Learning-Book.validation.json` verified via `Validate-Learning-Book.ps1/.sh`): (Route A) When `MAUI DevFlow` is installed and actively working on the target platform, run the app, tap the target control by `AutomationId`, verify live binding values from the visual tree, and capture a real screenshot into `Learning/Images/<ScreenName>-live.png`; or (Route B — Mandatory Fallback whenever DevFlow is unavailable) create `Learning/Mockups/<ScreenName>.html`, run `python .\Scripts\Capture-Mockup-Blocks.py` into `Learning/Images/`, embed the images in `Learning/Guides/*.md`, and run `python .\Scripts\Generate-Learning-Book-Pdf.py`. In Code Generation Mode (`studentCapabilityMode=false`), batching across layers MUST include this visual documentation and PDF compilation pipeline before declaring `Status: COMPLETE`.
- **Student Mode Bug Hand-Off**: In `studentCapabilityMode=true`, the agent must NEVER auto-fix UI or binding bugs discovered via `MAUI DevFlow`; it reports the visual-tree readout and screenshot to the student and sets `Status: BLOCKED` or `WAITING_FOR_STUDENT`.
- **Precedence over External Skills**: `maui-k12-baton-workflow` guardrails strictly override any external `dotnet/maui-labs` (`maui ai init`) skills (Vanilla C# MVVM and baton gates are never bypassed).
- **`SetProperty(ref ...)` Soft-Gate & ViewModel Scoping**: In ViewModels, prefer explicit 3-line setters (`if (_field == value) return; _field = value; OnPropertyChanged();`). If `SetProperty(ref _field, value)` is encountered or proposed before `Learning/Student-Mastery.md` records mastery of `ref`, do NOT fail the build (`Validate-Maui-ObsoleteApis.ps1/.sh` emits a non-blocking `[PEDAGOGICAL WARNING]` and exits `0`). Instead, issue a pedagogical warning to the student, explain the mechanism (`ref` parameter passing and backing field update), and ask the student whether they prefer to keep it or use the explicit 3-line setter. In Custom Views/Controls (`BindableObject`/`ContentView` in `Views/` or `Controls/`), this restriction does not apply.
- **Unit Test Provisioning, Management Modes & Blocking Gate (`includeTests` & `testManagementMode` in `.agents/MAUI-Agent-Mode.json`)**:
  - `includeTests` (boolean, default `true`): When `false`, ignore `testManagementMode` and skip unit tests.
  - `testManagementMode` (`"combined"` | `"agent"` | `"student"`, default `"combined"`): In `studentCapabilityMode=true`, `"combined"` has the agent create and explain tests at the end of each stage/slice while offering selected test cases to the student; `"agent"` has the agent write and document tests independently; `"student"` has the agent guide the student via Socratic dialogue to write the tests. In `studentCapabilityMode=false` (`MAXIMIZE CODE GENERATED`), when `includeTests=true`, the test writer is **ALWAYS `"agent"`** regardless of `testManagementMode`, and the agent must document all tests in `Learning/Test-Documentation.md`.
  - `Scripts/Ensure-Test-Project.ps1/.sh/.py` provisions `<AppName>.Tests` (`xUnit`), links it to `.sln`/`.slnx` and `<AppName>.csproj`, and adds the plain `net10.0` / `net11.0` target framework to the MAUI `.csproj` so xUnit compiles and runs tests directly against ViewModels/Services/Converters.
  - `Scripts/Validate-Tests.ps1/.sh/.py` blocks `Status: COMPLETE` when `includeTests=true` unless `*.Tests.csproj` exists, `Learning/Test-Documentation.md` is populated, and `dotnet test` passes with `Failed == 0` and `Passed >= 1`.
