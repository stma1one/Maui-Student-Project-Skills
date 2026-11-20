# MAUI K12 Baton Workflow Skill

Portable agent-skill package (v1.5.1) for teaching high-school students to build .NET MAUI projects through staged planning, concept gates, ownership negotiation, implementation, verification, and learning documentation.

The package is designed for:
- Antigravity project agents that read `AGENTS.md` and `.agents/skills`
- Codex local/project skills that read `SKILL.md`
- Claude Code setups that support project instructions and local skills
- Any coding agent where you can paste or reference an instruction file

## What This Skill Solves

Most coding agents move too quickly for students: they ask questions, propose architecture, explain concepts, generate code, and assign tasks all in one heavy response.

This skill forces a baton workflow:

```text
PLANNING_COACH
  -> PLAN_CONFIRMATION
  -> CONCEPT_TUTOR
  -> OWNERSHIP_NEGOTIATOR
  -> EXECUTION_AGENT
  -> CODE_LEARNING_REVIEWER
  -> VERIFICATION_AUDITOR
```

The student receives one cognitive step at a time.

The workflow treats theory and coding ability as separate evidence. Explaining a concept authorizes guided practice; only verified student-authored coding evidence plus theory evidence makes that concept routine-eligible for agent-owned repetition.

## Package Layout

```text
maui-k12-baton-workflow/
|-- README.md
|-- PACKAGE-MANIFEST.md
|-- AGENTS.md
|-- CLAUDE.md
|-- skills/
|   `-- maui-k12-baton-workflow/
|       |-- SKILL.md
|       |-- references/
|       |   |-- bagrut-5u-requirements.md
|       |   |-- maui-specialist-guardrails.md
|       |   `-- student-capability-gates.md
|       `-- evals/evals.json
|-- project-template/
|   |-- AGENTS.md
|   |-- .agents/
|   |   |-- MAUI-Agent-Mode.json
|   |   `-- templates/
|   |       `-- phase-status-template.md
|   |-- Learning/
|   |   |-- AI-And-External-Code-Attribution.md
|   |   |-- Bagrut-Compliance.md
|   |   |-- Current-Phase.md
|   |   |-- MAUI-Learning-Book.md
|   |   |-- Student-Mastery.md
|   |   `-- Test-Documentation.md
|   `-- Scripts/
|       |-- Audit-DI.ps1 / .sh
|       |-- Capture-Mockup-Blocks.py
|       |-- Check-Learning-Book-Prerequisites.py
|       |-- Ensure-Maui-DevFlow.ps1 / .sh / .py
|       |-- Ensure-Test-Project.ps1 / .sh / .py
|       |-- Generate-Architecture-Diagrams.ps1 / .sh / .py
|       |-- Generate-Learning-Book-Pdf.ps1 / .sh / .py
|       |-- Validate-Bagrut-Compliance.ps1 / .sh / .py
|       |-- Validate-Learning-Book.ps1 / .sh / .py
|       |-- Learning-Book-Requirements.txt
|       |-- Record-Learning-Change.ps1 / .sh
|       |-- Setup-Learning-Book.ps1 / .sh
|       |-- Setup-Skills.ps1 / .sh
|       |-- Validate-Maui-ObsoleteApis.ps1 / .sh
|       |-- Validate-Maui-Version.ps1 / .sh
|       |-- Validate-Maui-XamlResources.ps1 / .sh
|       `-- Validate-Tests.ps1 / .sh / .py
`-- scripts/
    |-- Install-Skill.ps1
    |-- Install-Skill.sh
    |-- Set-Maui-Agent-Mode.ps1
    |-- Set-Maui-Agent-Mode.sh
    |-- Run-Evals.py
    `-- golden-eval-responses.json

Companion Skill: `maui-step-guide-author` for source-grounded learning books, modular screen guides, generic HTML visual-model snapshots, and validated HTML/PDF book rendering.
```

## Quick Install & Upgrade In A MAUI Project

### Windows (PowerShell):

Fresh install (automatically provisions two layers when the project targets `net10.0` or `net11.0`, skipping `net9.0` and older targets: (1) Debug-only `Microsoft.Maui.DevFlow.Agent` `0.1.0-preview.14.26531.2` in `.csproj` and `MauiProgram.cs`, and (2) global `.NET MAUI DevFlow CLI` via `dotnet tool install -g Microsoft.Maui.Cli --prerelease`; pass `-SkipDevFlow` to opt out of all DevFlow provisioning or `-SkipCli` if working without global permissions):

```powershell
.\scripts\Install-Skill.ps1 -Target Project -ProjectPath C:\path\to\YourMauiProject
# Opt out of global CLI installation only (keep project NuGet):
.\scripts\Install-Skill.ps1 -Target Project -ProjectPath C:\path\to\YourMauiProject -SkipCli
# Opt out of automatic MAUI DevFlow injection entirely:
.\scripts\Install-Skill.ps1 -Target Project -ProjectPath C:\path\to\YourMauiProject -SkipDevFlow
```

Upgrade an existing project (refreshes `.agents/skills/*`, updates `Scripts/*`, upgrades DevFlow when available on `net10.0`/`net11.0`, and writes `AGENTS.md.new` if `AGENTS.md` changed while preserving student `Learning/*.md` and `MAUI-Agent-Mode.json`):

```powershell
.\scripts\Install-Skill.ps1 -Target Project -ProjectPath C:\path\to\YourMauiProject -Upgrade
```

Reliable Windows form when script execution is restricted:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Install-Skill.ps1 -Target Project -ProjectPath C:\path\to\YourMauiProject -Upgrade
```

### macOS / Linux (Bash):

Fresh install (pass `--skip-cli` to skip global `Microsoft.Maui.Cli` installation or `--skip-devflow` to opt out of automatic DevFlow injection):

```bash
chmod +x ./scripts/Install-Skill.sh
./scripts/Install-Skill.sh Project /path/to/YourMauiProject
# Opt out of global CLI installation only:
./scripts/Install-Skill.sh Project /path/to/YourMauiProject --skip-cli
# Opt out of automatic MAUI DevFlow injection:
./scripts/Install-Skill.sh Project /path/to/YourMauiProject --skip-devflow
```

Upgrade an existing project:

```bash
./scripts/Install-Skill.sh Project /path/to/YourMauiProject --upgrade
```

Then open the target project in your agent tool and ask it to read `AGENTS.md`.

The installer never overwrites an existing `AGENTS.md` (it writes `AGENTS.md.new` when the template has changed), `MAUI-Agent-Mode.json`, `Current-Phase.md`, `MAUI-Learning-Book.md`, `Student-Mastery.md`, `Bagrut-Compliance.md`, `AI-And-External-Code-Attribution.md`, or `Test-Documentation.md`. It always creates `Learning/Guides`, `Learning/Mockups`, `Learning/Images`, and `Learning/Diagrams`, provisions `<AppName>.Tests` (when `includeTests: true`), and cleanly replaces `.agents/skills/*` so removed skill files do not linger. Python 3 is optional for project installation: if Python 3 is missing, the installer attempts a best-effort automatic installation and falls back to native PowerShell/Bash provisioning so setup never fails.

### Agent Modes & Unit Test Configuration (`.agents/MAUI-Agent-Mode.json`)

The project's pedagogical and unit-testing behavior is controlled by `.agents/MAUI-Agent-Mode.json` (which only the instructor may modify via `Set-Maui-Agent-Mode.ps1` / `.sh`):

```json
{
  "studentCapabilityMode": true,
  "includeTests": true,
  "testManagementMode": "combined"
}
```

- **`studentCapabilityMode`** (`true` by default):
  - `true` (`Mode: MAXIMIZE STUDENT CAPABILITY`): Enforces one baton stage per response, concept gates, ownership negotiation, and `// TODO (Student)` core tasks.
  - `false` (`Mode: MAXIMIZE CODE GENERATED`): Batches implementation across layers, visual artifacts, unit tests, and PDF compilation in one workflow.
- **`includeTests`** (`true` by default):
  - When `true`, `Ensure-Test-Project.ps1/.sh` automatically provisions `<AppName>.Tests` (`xUnit`), links it to `.sln`/`.slnx` and `<AppName>.csproj`, and adds the plain `net10.0` / `net11.0` target framework to the MAUI `.csproj` so xUnit tests compile and run without an emulator. `Validate-Tests.ps1/.sh` enforces `Failed == 0`, `Passed >= 1`, and an updated `Learning/Test-Documentation.md` before `Status: COMPLETE`.
  - When `false`, `testManagementMode` is ignored and unit-test provisioning/validation is skipped.
- **`testManagementMode`** (`"combined"` | `"agent"` | `"student"`, default `"combined"`):
  - `"combined"` (Default): Agent creates core/scaffold tests, explains them at the end of each stage/slice, offers selected test cases to the student, and documents all tests in `Learning/Test-Documentation.md`.
  - `"agent"`: Agent writes and runs the xUnit tests independently and documents them in `Learning/Test-Documentation.md`.
  - `"student"`: Agent guides the student via Socratic dialogue to design and write the xUnit tests.
  - **`MAXIMIZE CODE GENERATED` Override:** When `studentCapabilityMode` is `false` and `includeTests` is `true`, the effective test writer is **always `"agent"`** regardless of `testManagementMode`, and all tests are documented in `Learning/Test-Documentation.md`.

Instructor mode-switching examples:

```powershell
# Student mode with combined test management (default):
.\scripts\Set-Maui-Agent-Mode.ps1 -Mode student -ProjectRoot C:\path\to\YourMauiProject -IncludeTests $true -TestManagementMode combined
# Code generation mode (agent automatically writes & documents all tests):
.\scripts\Set-Maui-Agent-Mode.ps1 -Mode code -ProjectRoot C:\path\to\YourMauiProject -IncludeTests $true
# Disable unit tests for a project:
.\scripts\Set-Maui-Agent-Mode.ps1 -Mode student -ProjectRoot C:\path\to\YourMauiProject -IncludeTests $false
```

```bash
./scripts/Set-Maui-Agent-Mode.sh true /path/to/YourMauiProject true combined
./scripts/Set-Maui-Agent-Mode.sh false /path/to/YourMauiProject true agent
./scripts/Set-Maui-Agent-Mode.sh true /path/to/YourMauiProject false combined
```

### Learning-book tools, Android screenshots & visual Architecture/UML PNGs

The checker never downloads learning-book browser binaries by default. When prerequisites are already available, it does nothing. When they are missing, it names the missing items and explains that installation can download browser binaries, use disk space, and change the selected Python environment.

Check the target project at any time:

```powershell
.\Scripts\Setup-Learning-Book.ps1
```

Install only after the user explicitly agrees:

```powershell
.\Scripts\Setup-Learning-Book.ps1 -InstallMissing
# Or install while running the package installer:
.\scripts\Install-Skill.ps1 -Target Project -ProjectPath C:\path\to\YourMauiProject -InstallLearningBookDependencies
```

```bash
./Scripts/Setup-Learning-Book.sh
./Scripts/Setup-Learning-Book.sh . --install-missing
# Or: ./scripts/Install-Skill.sh Project /path/to/YourMauiProject --install-learning-book-dependencies
```

Then generate the architecture diagrams (`Learning/Images/Screen-Flow.png` and `Learning/Images/Architecture-UML.png`), capture screen snapshots (including Android smartphone-framed `Learning/Images/<ScreenName>-android.png`), and compile the PDF book:

```powershell
.\Scripts\Generate-Architecture-Diagrams.ps1
python .\Scripts\Capture-Mockup-Blocks.py --mockup .\Learning\Mockups\<ScreenName>.html --screen <ScreenName>
python .\Scripts\Generate-Learning-Book-Pdf.py
.\Scripts\Validate-Learning-Book.ps1
.\Scripts\Validate-Tests.ps1
```

The generator writes `Learning/MAUI-Learning-Book.pdf` and `Learning/MAUI-Learning-Book.validation.json`. `Status: COMPLETE` is blocked until `dotnet build`, `Validate-Tests` (when `includeTests: true`), and `Validate-Learning-Book` all pass.

## Manual Install: Antigravity Project

1. Copy `project-template/AGENTS.md` to the target project root as `AGENTS.md`.
2. Copy `skills/maui-k12-baton-workflow/` to `<target-project>/.agents/skills/maui-k12-baton-workflow/`.
3. Copy `companion-skills/maui-step-guide-author/skills/maui-step-guide-author/` to `<target-project>/.agents/skills/maui-step-guide-author/`.
4. Copy `project-template/.agents/MAUI-Agent-Mode.json` to `<target-project>/.agents/MAUI-Agent-Mode.json`.
5. Copy `project-template/.agents/templates/phase-status-template.md` to `<target-project>/.agents/templates/phase-status-template.md`.
6. Copy the learning templates to `<target-project>/Learning/` and create `Learning/Guides`, `Learning/Mockups`, and `Learning/Images`.
7. Copy `project-template/Scripts/` to `<target-project>/Scripts/`.
8. Start a new session and verify the first assistant line is:

```text
Mode: MAXIMIZE STUDENT CAPABILITY
```

## Manual Install: Codex

### Project-local install

Use the same Antigravity project install above. Codex sessions that load project `AGENTS.md` and `.agents/skills` will pick up the workflow from the target repository.

### User-wide install

```powershell
.\scripts\Install-Skill.ps1 -Target Codex
```

## Manual Install: Claude Code

1. Copy `CLAUDE.md` to the target project root.
2. Copy `project-template/AGENTS.md` as `AGENTS.md` if your environment also reads AGENTS-style instructions.
3. Run `.\scripts\Install-Skill.ps1 -Target ClaudeCode` (or `./scripts/Install-Skill.sh ClaudeCode`) to install the skills into `~/.claude/skills/`.

## Running Package & Evaluation Validation

To validate all `evals.json` schemas, referenced files, shared script hashes, and assertion grader self-tests:

```bash
python3 ./scripts/Run-Evals.py
```

To grade a JSON file of captured agent responses (`{ "<eval_id>": "<response_text>" }`) against the deterministic assertions:

```bash
python3 ./scripts/Run-Evals.py --responses path/to/responses.json
```

## Creator & Attribution

Created by **Tal Simon** (2026).

If you use, adapt, or redistribute this package in your school, organization, or project, please preserve the [NOTICE](./NOTICE) and [LICENSE](./LICENSE) files and give credit to the original creator.

## License

This package is licensed under the [Apache License 2.0](./LICENSE). See `LICENSE` and `NOTICE` for full terms.
