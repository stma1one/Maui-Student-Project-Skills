# MAUI Specialist Guardrails

Read this reference during `PLANNING_COACH`, `EXECUTION_AGENT`, `CODE_LEARNING_REVIEWER`, or `VERIFICATION_AUDITOR` whenever the slice touches architecture, ViewModels, Services, SQLite, XAML, Shell navigation, tests, style resources, audit, or Hebrew learning documentation. This file is the **Single Source of Truth** for .NET MAUI technical guardrails.

## Architecture, Vanilla C# MVVM, And State

- Keep the project student-readable. Avoid enterprise abstractions unless they remove real complexity.
- **Vanilla C# MVVM Core (No MVVM Source Generators, But CommunityToolkit UI & Messaging Are Allowed):**
  - Implement `INotifyPropertyChanged` and `ICommand` (`Command` / `Command<T>`) explicitly using standard C# properties, backing fields, and command wiring.
  - Do **not** use MVVM source-generator shortcuts or base classes that hide property/command mechanics: `[ObservableProperty]`, `[RelayCommand]`, `[NotifyCanExecuteChangedFor]`, `[NotifyPropertyChangedFor]`, or `ObservableObject` / `ObservableValidator`.
  - **Allowed CommunityToolkit usage:**
    - `CommunityToolkit.Maui` UI controls, popups, behaviors, and converters are **allowed**.
    - `WeakReferenceMessenger` (`CommunityToolkit.Mvvm.Messaging`) is **allowed** as the modern, memory-safe replacement for obsolete `MessagingCenter` when decoupled messaging is genuinely needed.
- Use clear MVVM boundaries:
  - View: layout, controls, visual states, bindings, accessibility.
  - ViewModel: UI state, commands, validation, service coordination.
  - Service: data access, APIs, persistence, platform operations.
  - Model: data representation.
- Prefer constructor dependency injection. Never instantiate services (`new SomeService()`) inside ViewModels.
- Do not perform network, database, or file work in constructors. Use an explicit async lifecycle method (such as `InitializeAsync()` invoked from page lifecycle) with loading/error handling.
- Avoid `.Result` and `.Wait()`.
- Use `async Task` for async work; reserve `async void` for required event handlers.
- **No Obsolete MAUI APIs:**
  - Do not use `Page.IsBusy` or `IsBusy = true` on pages; use ViewModel `IsLoading` plus `ActivityIndicator`.
  - In .NET 10 MAUI, use `DisplayAlertAsync`, `DisplayActionSheetAsync`, and `DisplayPromptAsync` instead of obsolete synchronous-named `DisplayAlert`, `DisplayActionSheet`, or `DisplayPrompt`.
  - Use `*Async` animation methods (`FadeToAsync`, `ScaleToAsync`, `TranslateToAsync`, `RotateToAsync`) instead of obsolete `FadeTo`, `ScaleTo`, `TranslateTo`, or `RotateTo`.
  - Use `CollectionView` instead of obsolete `ListView` or `TableView`.
  - Do not use obsolete `MessagingCenter` (use direct MVVM/Service coordination, C# events, or `WeakReferenceMessenger` from `CommunityToolkit.Mvvm.Messaging`) or obsolete `Device.BeginInvokeOnMainThread` (use `MainThread.BeginInvokeOnMainThread`).
- **Property Setters & `SetProperty(ref ...)` Soft-Gate Policy:**
  - **ViewModel Scope Only:** This rule applies strictly to `ViewModel` classes and `BaseViewModel` (`ViewModels/*.cs` or `*ViewModel.cs`).
  - **Custom Views Exemption:** Custom controls and views in `Views/` or `Controls/` (`BindableObject` / `ContentView`) that use `SetValue` or internal helper methods are explicitly exempt from this rule.
  - **Soft-Gate Workflow (Advisory Warning & Student Choice):** In ViewModels, prefer starting students with explicit 3-line property setters (`if (_field == value) return; _field = value; OnPropertyChanged();`). When `SetProperty(ref _field, value)` is encountered or proposed before `Learning/Student-Mastery.md` records mastery of `ref` and `SetProperty`, do **not** fail the build (`Scripts/Validate-Maui-ObsoleteApis.ps1/.sh` emits a non-blocking `[PEDAGOGICAL WARNING]` and exits `0`). Instead, briefly explain how `ref` parameter passing and backing-field updates work inside `SetProperty` and ask the student to choose:
    - **Option A (אפשרות א'):** Replace with the explicit 3-line setter (`if (_field == value) return; _field = value; OnPropertyChanged();` — recommended for Bagrut clarity).
    - **Option B (אפשרות ב'):** Keep `SetProperty(ref _field, value)`, learn the `ref` concept now, and record it in `Learning/Student-Mastery.md` (and explain it in `Learning/MAUI-Learning-Book.md`).
- Prefer `ICommand.CanExecute` over explicit `IsEnabled` bindings in XAML buttons and interactive controls. Use `CanExecute` with a meaningful condition and refresh it via `ChangeCanExecute()` / `CanExecuteChanged` when relevant state changes.

## Targeted Documentation Verification (High-Friction Triggers)

Do not perform redundant web searches for routine C# or MVVM code.
However, you MUST actively query official documentation (Microsoft Learn for MAUI, Firebase for Google services) when encountering any of these **High-Friction Triggers**:

1. **Native & Storage NuGet Packages**:
   - When adding or choosing packages for SQLite, local storage, or platform bindings.
   - Purpose: Ensure zero package conflicts and correct platform provider bundles.
2. **Platform & Device-Specific Features**:
   - When using `WebView`, `MediaPicker`, `Geolocation`, `Permissions`, or native hardware controls.
   - Purpose: Ensure correct MAUI-specific XAML controls and lifecycle methods are used (not Web or standard desktop idioms).
3. **Cloud & Third-Party SDK Integration**:
   - When integrating Firebase, Firestore, Authentication providers, or Azure services in a MAUI client.
   - Purpose: Verify current recommended mobile/.NET SDK architecture, initialization hooks, and credentials handling.
4. **Platform Crash / Native Diagnostics**:
   - When encountering native symbol collisions, P/Invoke failures, or platform sandbox exceptions.

## Approved SQLite Stack (Non-Negotiable)

For any student project that persists data in SQLite, use only:

1. `sqlite-net-pcl` for basic CRUD operations with `SQLiteAsyncConnection`. Follow Microsoft's MAUI SQLite guide: https://learn.microsoft.com/en-us/dotnet/maui/data-cloud/database-sqlite?view=net-maui-10.0
2. `SQLiteNetExtensions` (and `SQLiteNetExtensions.Async` when using async relationship helpers such as `GetWithChildrenAsync`, `InsertWithChildrenAsync`, or `UpdateWithChildrenAsync` on `SQLiteAsyncConnection`) in addition to `sqlite-net-pcl` only when the model needs relationships:
   - One-to-one: https://www.codejourney.net/sqlite-net-extensions-one-to-one-relationships/
   - One-to-many: https://www.codejourney.net/sqlite-net-extensions-one-to-many-relationships/
   - Many-to-many: https://www.codejourney.net/sqlite-net-extensions-many-to-many-relationships/
   - Note: You may also manage 1:N foreign-key queries explicitly using `SQLiteAsyncConnection.Table<T>().Where(...)` in the Service layer so students clearly see how foreign keys work.

Do not use or add Entity Framework Core SQLite (`Microsoft.EntityFrameworkCore.Sqlite`), `Microsoft.Data.Sqlite`, `System.Data.Sqlite`, Dapper, LiteDB, or any other ORM/provider. Do not replace `sqlite-net-pcl` with `SQLiteNetExtensions`; the extension packages are strictly additive.

Implementation rules:
- Keep database operations in a Service/Repository, never in a View or ViewModel.
- Always use async APIs (`SQLiteAsyncConnection`); never block the UI thread with synchronous `SQLiteConnection`, `.Result`, or `.Wait()`.
- For relationships, explicitly identify the cardinality (`[OneToOne]`, `[OneToMany]`, `[ManyToMany]`, `[ForeignKey]`) and either use `SQLiteNetExtensions.Async` helpers on `SQLiteAsyncConnection` or explicit async queries in the Service. Never assume relationship loading happens automatically.

## XAML UI

- For Hebrew-first apps, set `FlowDirection="RightToLeft"` at Shell or page level. Do not force RTL onto URLs, emails, code, or identifiers.
- Prefer compiled bindings with `x:DataType` when the binding context is known.
- Always type `DataTemplate` contexts.
- Do not use untyped bindings to silence warnings.
- Use the simplest suitable layout: `Grid`, `VerticalStackLayout`, `HorizontalStackLayout`, `FlexLayout`, or `CollectionView`.
- Avoid arbitrary fixed page dimensions.
- Important controls need meaningful labels, readable states, and accessible touch targets.
- Prefer ViewModel validation state plus binding, `DataTrigger`, or `VisualStateManager`.
- Every `StaticResource`, `DynamicResource`, `BasedOn`, and `x:Key` reference must resolve in scope (either within the same XAML file's `Resources` or in `App.xaml` / `Resources/Styles/*.xaml`).
- Put shared styles in `Resources/Styles/Styles.xaml`, shared colors in `Resources/Styles/Colors.xaml`, and page-specific styles in page resources.

## Shell Navigation

- Use Shell as the primary navigation system for Shell-based student projects.
- Root hierarchy belongs in `AppShell.xaml`.
- Detail pages use registered routes.
- Prefer route names based on `nameof(PageType)` when practical.
- Navigate with `Shell.Current.GoToAsync(...)`; back navigation uses `".."`.
- Pass small parameters through `Dictionary<string, object>`.
- Prefer passing IDs over large objects when the destination can load data itself.
- Use `IQueryAttributable` or another current documented Shell mechanism when receiving parameters.
- Register Pages and ViewModels in DI when Shell or constructors need to resolve them.
- Do not create an `INavigationService` wrapper unless tests or project requirements justify it.

## Tests

- Use xUnit for ViewModel and Service behavior.
- Use Arrange, Act, Assert.
- Prefer descriptive names such as `SaveCommand_WhenFormInvalid_CannotExecute`.
- Async tests use `async Task`.
- Test behavior, not XAML visual trees.
- Cover initial state, success, failure, validation, loading state, error state, collection updates, command behavior, and `CanExecute` where relevant.
- Use simple manual fakes when mocking libraries are not allowed.
- Reject weak tests such as `Assert.NotNull(vm)` when they cannot fail for the behavior under test.

## Verification Audit

Before declaring `Status: COMPLETE` in `VERIFICATION_AUDITOR`, verify with evidence:

```text
1. Target framework/version (net8.0 / net9.0 / net10.0 / net11.0)
2. Current MAUI compatibility (no obsolete APIs)
3. Build (dotnet build)
4. Architecture boundaries (no Services instantiated in ViewModels)
5. DI registration in MauiProgram.cs
6. Navigation routes & DI
7. Compiled Bindings (x:DataType)
8. Styles/resources scope resolution
9. State/commands & CanExecute
10. Async/error handling (no .Result / .Wait() / constructor I/O)
11. Tests (dotnet test)
12. Learning documentation, screen visual artifacts (`Learning/Images/`), and compiled PDF learning book (`Learning/MAUI-Learning-Book.pdf` + `Learning/MAUI-Learning-Book.validation.json`)
```

Run available checks:

**Windows (PowerShell):**
```powershell
dotnet build
dotnet test
.\Scripts\Validate-Maui-Version.ps1
.\Scripts\Validate-Maui-ObsoleteApis.ps1
.\Scripts\Validate-Maui-XamlResources.ps1
.\Scripts\Audit-DI.ps1
.\Scripts\Validate-Bagrut-Compliance.ps1
.\Scripts\Generate-Architecture-Diagrams.ps1
python .\Scripts\Generate-Learning-Book-Pdf.py
.\Scripts\Validate-Learning-Book.ps1
```

**macOS / Linux (Bash):**
```bash
dotnet build
dotnet test
./Scripts/Validate-Maui-Version.sh
./Scripts/Validate-Maui-ObsoleteApis.sh
./Scripts/Validate-Maui-XamlResources.sh
./Scripts/Audit-DI.sh
./Scripts/Validate-Bagrut-Compliance.sh
./Scripts/Generate-Architecture-Diagrams.sh
python3 ./Scripts/Generate-Learning-Book-Pdf.py
./Scripts/Validate-Learning-Book.sh
```

Never claim `Status: COMPLETE` without concrete execution evidence — including both a passing `dotnet build` and a compiled, validated `Learning/MAUI-Learning-Book.pdf` (`Learning/MAUI-Learning-Book.validation.json` passing and at least one image in `Learning/Images/` for every screen). If a check cannot run in the current environment, state the limitation clearly and use `Status: READY_TO_VERIFY`. If any check fails, use `Status: BLOCKED`.

In Student Capability Mode, also verify:
- the plan was approved or planning decisions were documented
- concept-gate evidence exists
- ownership split was chosen before execution
- agent-owned and student-owned tasks are recorded
- `Learning/Student-Mastery.md` keeps theory evidence separate from applied coding evidence with a real `Evidence source`
- no agent-generated, copied, or merely explained code is recorded as applied coding evidence
- agent-owned routine work is limited to concepts recorded with both evidence tracks and `Routine eligibility: Yes`

## Learning Documentation (Hebrew with English Identifiers)

Maintain `Learning/MAUI-Learning-Book.md` as append-only.

**Language Rule (Mandatory):**
- Write all explanations, architectural rationale, and guidance in `Learning/MAUI-Learning-Book.md` and `Learning/Guides/<ScreenName>-Guide.md` in **Hebrew**.
- Keep all C#, XAML, SQL, and .NET code identifiers, class names, properties, attributes, and file paths in **English**.

For each meaningful code change, document:
- current phase and baton workflow stage
- planning decision or concept gate
- ownership split (what the student did vs. what the agent changed)
- why the architecture was chosen
- how to verify
- Do not write generic textbook lessons. Teach the actual project change.

### Step-by-Step Learning Books and UI Guides

When documenting a screen, page, UI feature, or existing-project learning journey, use the `maui-step-guide-author` methodology:
- For an existing project, map current files and behavior with the student before proposing milestones to the end goal.
- Do not dump monolithic XAML or ViewModel files. Provide small source-grounded blocks with their file/layer, rationale, evidence, and a student checkpoint.
- Create an HTML visual model at `Learning/Mockups/<ScreenName>.html` only when it teaches the screen composition; label it as a model rather than emulator evidence.
- Capture the marked overview and individual blocks with `Capture-Mockup-Blocks.py`, then embed the generated images in the matching guide sections.
- Write all guide prose in **Hebrew** while preserving XAML elements, C# identifiers, and commands in **English**.
- Save each screen guide at `Learning/Guides/<ScreenName>-Guide.md`, index it in `Learning/MAUI-Learning-Book.md`, and require the generated book validation report to pass before publication.

## Student Review Tone

Use supportive review:

```text
What is good
What to improve
Why it matters
Smallest useful fix
```

Do not help disguise generated work. Help the student understand, simplify, and explain it.

## 10. MAUI DevFlow Runtime Inspection & External Skill Precedence

- **Allowed Debug-Only Package (`.NET 10` / `.NET 11` Only)**: `Microsoft.Maui.DevFlow.Agent` ([NuGet](https://www.nuget.org/packages/Microsoft.Maui.DevFlow.Agent/), [Microsoft Learn DevFlow Docs](https://learn.microsoft.com/en-us/dotnet/maui/developer-tools/devflow/?view=net-maui-10.0)) is explicitly permitted for live visual-tree inspection, binding verification, UI automation, and screenshot capture on `net10.0` and `net11.0` projects, provided:
  1. In `.csproj`, the `PackageReference` is strictly conditioned on `Debug` (`Condition="'$(Configuration)' == 'Debug'"` on either the `<ItemGroup>` or `<PackageReference>`).
  2. In `MauiProgram.cs`, `using Microsoft.Maui.DevFlow.Agent;` and `builder.AddMauiDevFlowAgent();` are wrapped strictly inside `#if DEBUG ... #endif`.
  3. The package is documented in `Learning/AI-And-External-Code-Attribution.md` (with no inline AI attribution comments in `.cs` or `.xaml`).
- **Two-Layer TFM-Aware Provisioning & Opt-Out (`Scripts/Ensure-Maui-DevFlow.py` / `.ps1` / `.sh`)**: Invoked by `Install-Skill.ps1/.sh` and `Scripts/Setup-Skills.ps1/.sh` (unless opted out with `-SkipDevFlow` / `--skip-devflow` / `--no-devflow`). It checks `<TargetFramework>` / `<TargetFrameworks>` first and provisions **two layers** when the project targets `net10.0` or `net11.0` (skipping `net9.0` and older targets such as `net9.0-android`):
  1. **Project Layer (NuGet):** Injects the pinned `0.1.0-preview.14.26531.2` `Microsoft.Maui.DevFlow.Agent` package into `.csproj` (`Condition="'$(Configuration)' == 'Debug'"`) and `#if DEBUG` `builder.AddMauiDevFlowAgent();` into `MauiProgram.cs`.
  2. **Machine Layer (Global CLI):** Installs or updates the global `.NET MAUI DevFlow CLI` (`dotnet tool install -g Microsoft.Maui.Cli --prerelease` / `dotnet tool update -g Microsoft.Maui.Cli --prerelease` when `-Upgrade` / `--upgrade` is passed). Use `-SkipCli` / `--skip-cli` (`MAUI_SKIP_DEVFLOW_CLI=1`) when working without global tool permissions, or `--remove` / `-Remove` to remove project DevFlow injection.
- **Release Leak Validation**: `Scripts/Validate-Maui-ObsoleteApis.ps1/.sh` fails with `[RELEASE LEAK]` if `Microsoft.Maui.DevFlow` appears in `.csproj` without a strict positive `Debug` condition (blocking `Condition="'$(Configuration)' != 'Debug'"`) or if `AddMauiDevFlowAgent()` / `using Microsoft.Maui.DevFlow` is called outside `#if DEBUG` (blocking `#if !DEBUG`, `#else`, and `#elif`).
- **Stage 7 Mandatory Visual & PDF Blocking Gate (`VERIFICATION_AUDITOR` — Android + Architecture/UML PNGs + PDF)**: `Status: COMPLETE` is strictly blocked until one of the two visual routes is completed for every screen, the Architecture & UML visual PNGs are generated, AND the PDF learning book is compiled and validated:
  - **Route A (Live `MAUI DevFlow` / Android Emulator — when installed and working):** Prefer running on Android (`dotnet build -t:Run -f net10.0-android` + `adb reverse tcp:9223 tcp:9223`) and capturing `Learning/Images/<ScreenName>-android.png` via `maui devflow MAUI screenshot` or `adb exec-out screencap -p > Learning/Images/<ScreenName>-android.png`. Never rely solely on a Windows desktop (`*-windows.png`) screenshot; if testing on Windows without a live Android emulator, also run `Capture-Mockup-Blocks.py` to generate the Android 14 smartphone-framed `<ScreenName>-android.png`.
  - **Route B (Mandatory Fallback — REQUIRED whenever `MAUI DevFlow` or an Android emulator is unavailable):** Create `Learning/Mockups/<ScreenName>.html`, run `python .\Scripts\Capture-Mockup-Blocks.py` to capture `<ScreenName>-overview.png`, `<ScreenName>-android.png`, and block images into `Learning/Images/`, embed the images into `Learning/Guides/*.md`, run `.\Scripts\Generate-Architecture-Diagrams.ps1` (producing `Learning/Images/Screen-Flow.png` and `Learning/Images/Architecture-UML.png`), and run `python .\Scripts\Generate-Learning-Book-Pdf.py` + `.\Scripts\Validate-Learning-Book.ps1/.sh`. `Status: COMPLETE` is permitted ONLY when `Learning/MAUI-Learning-Book.pdf` exists and is up to date, `Learning/Images/` has Android/mobile screen images plus `Screen-Flow.png` and `Architecture-UML.png`, and `Learning/MAUI-Learning-Book.validation.json` reports `"passed": true`.
- **Student Mode Non-Auto-Fix Rule**: When `studentCapabilityMode=true`, any UI or binding defect discovered via `MAUI DevFlow` must be handed back to the student with the visual-tree readout and screenshot (`Status: BLOCKED` or `WAITING_FOR_STUDENT`). The agent must never fix student-owned code on the student's behalf.
- **Strict Precedence over `dotnet/maui-labs` (`maui ai init`)**: External skills from [`dotnet/maui-labs`](https://github.com/dotnet/maui-labs) are subordinate to this file. If an external skill suggests `[ObservableProperty]`, `[RelayCommand]`, `ObservableObject`, or skipping baton stages, reject that suggestion and enforce Vanilla C# MVVM and the K12 baton workflow.
