# Package Manifest

Package: MAUI K12 Baton Workflow Skill
Version: 1.4.1
Status: classroom-ready

## Purpose

Reusable agent workflow for .NET MAUI high-school student projects. It prevents coding agents from overwhelming students by splitting feature work into planning, confirmation, concept teaching, ownership negotiation, execution, code learning review, and verification stages, with optional live MAUI DevFlow runtime verification (when installed and supported on the active target platform), Ministry of Education 5-unit (883589) compliance tracking, and source-grounded Hebrew learning books and validated PDF compilation.

## Complete Package File Inventory (88 Files)

```text
.gitattributes
.gitignore
AGENTS.md
AUTHORS.md
CITATION.cff
CLAUDE.md
LICENSE
NOTICE
PACKAGE-MANIFEST.md
README.md
companion-skills/maui-step-guide-author/Install-Skill.ps1
companion-skills/maui-step-guide-author/Install-Skill.sh
companion-skills/maui-step-guide-author/PACKAGE-MANIFEST.md
companion-skills/maui-step-guide-author/README.md
companion-skills/maui-step-guide-author/scripts/Install-Skill.ps1
companion-skills/maui-step-guide-author/scripts/Install-Skill.sh
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/SKILL.md
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/evals/evals.json
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/references/bagrut-portfolio-structure.md
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/references/guide-template.md
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/references/html-mockup-guide.md
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/capture_mockup_blocks.py
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/ensure_maui_devflow.py
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/ensure_test_project.py
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/generate_architecture_diagrams.py
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/generate_book_pdf.py
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/requirements-learning-book.txt
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/validate_bagrut_compliance.py
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/validate_learning_book.py
companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/validate_tests.py
project-template/.agents/MAUI-Agent-Mode.json
project-template/.agents/templates/phase-status-template.md
project-template/AGENTS.md
project-template/Learning/AI-And-External-Code-Attribution.md
project-template/Learning/Bagrut-Compliance.md
project-template/Learning/Current-Phase.md
project-template/Learning/MAUI-Learning-Book.md
project-template/Learning/Student-Mastery.md
project-template/Learning/Test-Documentation.md
project-template/Scripts/Audit-DI.ps1
project-template/Scripts/Audit-DI.sh
project-template/Scripts/Capture-Mockup-Blocks.py
project-template/Scripts/Check-Learning-Book-Prerequisites.py
project-template/Scripts/Ensure-Maui-DevFlow.ps1
project-template/Scripts/Ensure-Maui-DevFlow.py
project-template/Scripts/Ensure-Maui-DevFlow.sh
project-template/Scripts/Ensure-Test-Project.ps1
project-template/Scripts/Ensure-Test-Project.py
project-template/Scripts/Ensure-Test-Project.sh
project-template/Scripts/Generate-Architecture-Diagrams.ps1
project-template/Scripts/Generate-Architecture-Diagrams.py
project-template/Scripts/Generate-Architecture-Diagrams.sh
project-template/Scripts/Generate-Learning-Book-Pdf.ps1
project-template/Scripts/Generate-Learning-Book-Pdf.py
project-template/Scripts/Generate-Learning-Book-Pdf.sh
project-template/Scripts/Learning-Book-Requirements.txt
project-template/Scripts/Record-Learning-Change.ps1
project-template/Scripts/Record-Learning-Change.sh
project-template/Scripts/Setup-Learning-Book.ps1
project-template/Scripts/Setup-Learning-Book.sh
project-template/Scripts/Setup-Skills.ps1
project-template/Scripts/Setup-Skills.sh
project-template/Scripts/Validate-Bagrut-Compliance.ps1
project-template/Scripts/Validate-Bagrut-Compliance.py
project-template/Scripts/Validate-Bagrut-Compliance.sh
project-template/Scripts/Validate-Learning-Book.ps1
project-template/Scripts/Validate-Learning-Book.py
project-template/Scripts/Validate-Learning-Book.sh
project-template/Scripts/Validate-Maui-ObsoleteApis.ps1
project-template/Scripts/Validate-Maui-ObsoleteApis.sh
project-template/Scripts/Validate-Maui-Version.ps1
project-template/Scripts/Validate-Maui-Version.sh
project-template/Scripts/Validate-Maui-XamlResources.ps1
project-template/Scripts/Validate-Maui-XamlResources.sh
project-template/Scripts/Validate-Tests.ps1
project-template/Scripts/Validate-Tests.py
project-template/Scripts/Validate-Tests.sh
scripts/Install-Skill.ps1
scripts/Install-Skill.sh
scripts/Run-Evals.py
scripts/Set-Maui-Agent-Mode.ps1
scripts/Set-Maui-Agent-Mode.sh
scripts/golden-eval-responses.json
skills/maui-k12-baton-workflow/SKILL.md
skills/maui-k12-baton-workflow/evals/evals.json
skills/maui-k12-baton-workflow/references/bagrut-5u-requirements.md
skills/maui-k12-baton-workflow/references/maui-specialist-guardrails.md
skills/maui-k12-baton-workflow/references/student-capability-gates.md
```

## Skill Metadata

Name:

```text
maui-k12-baton-workflow
```

Companion Skill:

```text
maui-step-guide-author (v1.4.1)
```

## Required Target Project Files (Installed by `Install-Skill`)

```text
AGENTS.md
.agents/skills/maui-k12-baton-workflow/SKILL.md
.agents/skills/maui-k12-baton-workflow/references/bagrut-5u-requirements.md
.agents/skills/maui-k12-baton-workflow/references/maui-specialist-guardrails.md
.agents/skills/maui-k12-baton-workflow/references/student-capability-gates.md
.agents/skills/maui-step-guide-author/SKILL.md
.agents/skills/maui-step-guide-author/references/bagrut-portfolio-structure.md
.agents/skills/maui-step-guide-author/references/guide-template.md
.agents/skills/maui-step-guide-author/references/html-mockup-guide.md
.agents/skills/maui-step-guide-author/scripts/*
.agents/MAUI-Agent-Mode.json
.agents/templates/phase-status-template.md
Learning/Current-Phase.md
Learning/MAUI-Learning-Book.md
Learning/Student-Mastery.md
Learning/Bagrut-Compliance.md
Learning/AI-And-External-Code-Attribution.md
Learning/Test-Documentation.md
Learning/Guides/
Learning/Mockups/
Learning/Images/
Learning/Diagrams/
Scripts/*
```
*(Note: `evals/` directories and `Set-Maui-Agent-Mode.*` instructor scripts are intentionally excluded from student project installations).*

## 1.4.1 Release Notes (TFM Gating, Opt-Out/Conditional DevFlow, Leak Hardening, Version Pinning & Optional Python)

- **.NET 10 / .NET 11 TargetFramework Check (`Ensure-Maui-DevFlow.py` / `.ps1` / `.sh`):** Verifies that the target `.csproj` targets `net10.0` or `net11.0` exclusively before injecting `Microsoft.Maui.DevFlow.Agent`. Projects targeting `net9.0` or earlier (such as `net9.0-android`) are automatically skipped (`[SKIP]`) for both `.csproj` and `MauiProgram.cs` so builds never break on unsupported frameworks.
- **Two-Layer DevFlow Provisioning, Opt-Out (`-SkipCli` / `-SkipDevFlow`) & Mandatory Android Visual + Diagram PNG + PDF Blocking Gate:** Added two-layer DevFlow provisioning in `Ensure-Maui-DevFlow.py/.ps1/.sh`, `Install-Skill.ps1/.sh`, and `Setup-Skills.ps1/.sh`: (1) Project layer (`Microsoft.Maui.DevFlow.Agent` NuGet in `.csproj` and `MauiProgram.cs`) and (2) Machine layer (`dotnet tool install -g Microsoft.Maui.Cli --prerelease` via `Ensure-DevFlowCli` / `ensure_devflow_cli`), with `-SkipCli` / `--skip-cli` for environments without global permissions and `-SkipDevFlow` / `--skip-devflow` (`--no-devflow`) or `-Remove` / `--remove` (`--disable`) to opt out or remove DevFlow. Stage 7 (`VERIFICATION_AUDITOR`) and Code Generation Mode enforce a **mandatory blocking gate** requiring either Route A (live `MAUI DevFlow` / Android emulator screenshot into `Learning/Images/<ScreenName>-android.png`) or Route B (mandatory fallback: `Learning/Mockups/<ScreenName>.html` + `Capture-Mockup-Blocks.py` producing an Android 14 smartphone-framed `<ScreenName>-android.png` + guide image embedding), visual PNG diagrams (`Learning/Images/Screen-Flow.png` and `Learning/Images/Architecture-UML.png` via `Generate-Architecture-Diagrams.py`), and `Generate-Learning-Book-Pdf.py` + `Validate-Learning-Book.ps1/.sh` (verifying Android/mobile images per screen, diagram PNGs, and an existing, up-to-date `Learning/MAUI-Learning-Book.pdf` with `"passed": true` in `Learning/MAUI-Learning-Book.validation.json`) before declaring `Status: COMPLETE`.
- **Configurable xUnit Test Provisioning, Management Modes & Blocking Gate (`includeTests` & `testManagementMode`):** Added `"includeTests": true` and `"testManagementMode": "combined"` (`"combined"` | `"agent"` | `"student"`) to `.agents/MAUI-Agent-Mode.json` and `Set-Maui-Agent-Mode.ps1/.sh`. When `includeTests=false`, `testManagementMode` is ignored and tests are skipped. When `studentCapabilityMode=false` (`MAXIMIZE CODE GENERATED`) and `includeTests=true`, the effective test writer is **always `"agent"`** regardless of `testManagementMode`, and all tests are documented in `Learning/Test-Documentation.md`. `Ensure-Test-Project.ps1/.sh/.py` automatically provisions `<AppName>.Tests` (`xUnit`), links it to `.sln`/`.slnx` and `<AppName>.csproj`, and adds the plain `net10.0` / `net11.0` target framework (with conditioned `<OutputType>` and `Platforms/**` exclusion) to the MAUI `.csproj`. `Validate-Tests.ps1/.sh/.py` blocks `Status: COMPLETE` when `includeTests=true` unless `*.Tests.csproj` exists, `Learning/Test-Documentation.md` is populated, and `dotnet test` passes with `Failed == 0` and `Passed >= 1`.
- **`SetProperty(ref ...)` ViewModel Soft-Gate & `Student-Mastery.md` Check:** `Validate-Maui-ObsoleteApis.ps1/.sh` scopes `SetProperty(ref ...)` detection strictly to `ViewModels/` and `*ViewModel.cs` (exempting `Views/`, `Controls/`, `Platforms/`), checks `Learning/Student-Mastery.md` for `ref` / `SetProperty` mastery, and emits a non-blocking `[PEDAGOGICAL WARNING]` (exiting `0`) when not yet mastered so the agent can offer the student a pedagogical choice in `CODE_LEARNING_REVIEWER`.
- **Hardened Release Leak Validation (`Validate-Maui-ObsoleteApis.ps1` & `.sh`):** Rejects negated or widened conditions such as `Condition="'$(Configuration)' != 'Debug'"`, `Condition="'$(Configuration)' == 'Debug' Or '$(Configuration)' == 'Release'"`, `#if !DEBUG`, `#if DEBUG || RELEASE`, `#else`, and `#elif`. `Validate-Maui-ObsoleteApis.sh` now includes a full POSIX `awk` fallback so Release leak validation never skips silently when Python is not installed.
- **Deterministic Initial Version Locking (`0.1.0-preview.14.26531.2`):** Initial installation (`Install-Skill`, `Setup-Skills`, `Ensure-Maui-DevFlow` without `--upgrade`) always injects the pinned classroom baseline version `0.1.0-preview.14.26531.2` even when online, guaranteeing identical versions across students installing on different days. Online NuGet upgrades are applied only when `--upgrade` / `-Upgrade` is explicitly passed.
- **Optional Python with Auto-Install Attempt & Native Fallback:** Python is no longer mandatory to install the skill in a `.NET MAUI` project. When Python 3 is missing, `Ensure-Maui-DevFlow.ps1/.sh` and `Setup-Learning-Book.ps1/.sh` first attempt a best-effort automatic Python 3 installation (`winget` / `brew` / `apt-get` / `dnf` / `apk`), and if Python remains unavailable, `Ensure-Maui-DevFlow.ps1/.sh` falls back to native PowerShell / Bash provisioning while `Setup-Learning-Book.ps1/.sh` warns without failing the project installation.

## 1.4.0 Release Notes (MAUI DevFlow & Bagrut 883589 Refinements)

- **Automatic Project DevFlow Provisioning & Version Check (`Ensure-Maui-DevFlow.py` / `.ps1` / `.sh`):** Automatically injects `Microsoft.Maui.DevFlow.Agent` (`0.1.0-preview.14.26531.2`) into compatible `.NET 10+` `.csproj` files under `Condition="'$(Configuration)' == 'Debug'"` and `builder.AddMauiDevFlowAgent();` into `MauiProgram.cs` under `#if DEBUG` during `Project` installation (`Install-Skill.ps1/.sh` and `Setup-Skills.ps1/.sh`, unless opted out via `-SkipDevFlow` / `--skip-devflow`). Checks NuGet (with offline fallback) to suggest or apply (`--upgrade` / `-Upgrade`) version upgrades when newer preview or stable releases are available.
- **Release Leak Protection & Guardrail Precedence:** `Validate-Maui-ObsoleteApis.ps1/.sh` fails with `[RELEASE LEAK]` if `Microsoft.Maui.DevFlow` is referenced without a strict `Debug` condition or if `AddMauiDevFlowAgent()` is called outside `#if DEBUG`. `maui-k12-baton-workflow` rules take strict precedence over external `dotnet/maui-labs` (`maui ai init`) skills.
- **Live Stage 7 Verification & Pedagogical Bug Hand-Off:** When `MAUI DevFlow` is installed and working on the active target, `VERIFICATION_AUDITOR` inspects the live visual tree, triggers controls by `AutomationId`, and captures real screenshots into `Learning/Images/` (keeping HTML mockups as fallback when DevFlow or an emulator is unavailable). In `studentCapabilityMode=true`, any UI/binding bug discovered via `MAUI DevFlow` is reported to the student (`WAITING_FOR_STUDENT` / `BLOCKED`) and never auto-fixed by the agent.
- **Ministry of Education 5-Unit Smartphone Rubric (883589) Alignment:** Tracks Thresholds 1–4, implementing **at least ONE** (`>= 1`) AI path in Section 5 (`AI-1`..`AI-4`, which counts as 1 topic in Section 6, while allowing and suggesting optional multi-path/component enrichment), Section 6 topics (omitting Android-only `ContentProvider`), Section 7 database persistence (`SQLite` or remote synchronized DB granting +2 topics in Section 10), and Section 8 advanced combinations.
- **Static Declaration Honesty in `Validate-Bagrut-Compliance.py`:** Never outputs `RESULT: PASS`; outputs `RESULT: DECLARATION_CHECK_OK` / `SUBMISSION_DECLARATION_OK` with an explicit disclaimer that table declaration checks do not prove implementation correctness.
- **Separate AI & External Code Attribution Log (Zero Inline AI Comments):** Records all AI-scaffolded and external code blocks (including `Microsoft.Maui.DevFlow.Agent`) in `Learning/AI-And-External-Code-Attribution.md`.

## 1.3.0 Release Notes (Ministry of Education 5-Unit Capstone 883589 & Architecture Diagrams)

- **5-Unit Smartphone Programming Rubric (883589) Integration (`references/bagrut-5u-requirements.md` & `Learning/Bagrut-Compliance.md`):** Adds structured tracking and proactive pedagogical reminders for mandatory thresholds (`REQ-1`..`REQ-4`), Section 5 AI paths (`AI-1`..`AI-4`), Section 6 core MAUI topics, Section 7 local/remote-sync database requirements, Section 8 advanced elective combinations (Sections 9 & 10), and the 8 mandatory Project Portfolio chapters (`DOC-1`..`DOC-8`).
- **Separate AI & External Code Attribution (`Learning/AI-And-External-Code-Attribution.md`):** Establishes the strict rule that `.cs` and `.xaml` source files must never contain inline AI attribution comments (`// Generated by AI`), centralizing all AI/external code disclosures, student modifications, oral-exam preparation notes (25% "שליטה בקוד"), and APA bibliography entries in a dedicated portfolio document.
- **Automated Mermaid Architecture Diagrams (`Generate-Architecture-Diagrams.py` / `.ps1` / `.sh`):** Parses project C# and XAML files to generate `Learning/Diagrams/Screen-Flow.mmd`, `Learning/Diagrams/Architecture-UML.mmd`, `Learning/Diagrams/Architecture-Diagram-Prompts.md`, and `Learning/Diagrams/Architecture-Preview.html` for Chapter 3 of the 883589 Project Portfolio.

## 1.2.0 Release Notes (Vanilla C# MVVM Policy, Two-Track Mastery Gates & Validation Suite)

- **Vanilla C# MVVM Policy (No MVVM Source Generators; CommunityToolkit UI & `WeakReferenceMessenger` Allowed):** Enforces explicit `INotifyPropertyChanged` (`OnPropertyChanged([CallerMemberName])`, preferring explicit 3-line property setters in ViewModels with a non-blocking `[PEDAGOGICAL WARNING]` soft-gate and student choice when `SetProperty(ref _field, value)` is used before `ref` is mastered in `Learning/Student-Mastery.md`, while exempting Custom Views/Controls in `Views/` or `Controls/`) and explicit `ICommand` / `Command` with `CanExecute`. Disallows MVVM source-generator attributes and base classes (`[ObservableProperty]`, `[RelayCommand]`, `[NotifyCanExecuteChangedFor]`, `[NotifyPropertyChangedFor]`, `ObservableObject`, `ObservableValidator`), while explicitly permitting `CommunityToolkit.Maui` UI controls, behaviors, and converters as well as `WeakReferenceMessenger` (`CommunityToolkit.Mvvm.Messaging`) as the modern, memory-safe replacement for obsolete `MessagingCenter`. Enforced by `Validate-Maui-ObsoleteApis.ps1/.sh`.
- **Two-Track Student Mastery & Anti-Bypass Enforcement (`references/student-capability-gates.md` & `Learning/Student-Mastery.md`):** Separates `Theory evidence` from student-authored `Applied coding evidence` (requiring a verifiable project file/method in `Evidence source` before marking `Level: Can work independently` and `Routine eligibility: Yes`), blocks student attempts to switch `studentCapabilityMode` in chat or bypass `// TODO (Student)` tasks with `"do it"` / `"continue"`, and enforces one baton stage per response.
- **Non-Negotiable SQLite Stack & Cross-Platform Validation Scripts:** Standardizes SQLite persistence on `sqlite-net-pcl` (`SQLiteAsyncConnection`) plus additive `SQLiteNetExtensions` / `SQLiteNetExtensions.Async` for relationships, and ships cross-platform PowerShell/Bash validators (`Validate-Maui-Version`, `Validate-Maui-ObsoleteApis`, `Validate-Maui-XamlResources`, `Audit-DI`) and deterministic evaluation grading (`scripts/Run-Evals.py`).

## License

Licensed under the Apache License, Version 2.0. Copyright 2026 Tal Simon. See `LICENSE` and `NOTICE` for details.
