#!/usr/bin/env python3
"""
Run-Evals.py
------------
Deterministic validator and evaluation assertion grader for the MAUI K12 Baton Workflow package.

Capabilities:
1. Validates schema and assertions of all `evals.json` files in the repository.
2. Verifies that any file path listed in an eval's `"files"` array exists in the repository.
3. Verifies byte-for-byte parity between shared scripts in `companion-skills/` and `project-template/Scripts/`,
   and between `project-template/Learning/AI-And-External-Code-Attribution.md` and `Setup-Skills.ps1/.sh`.
4. Verifies 1-to-1 file inventory accuracy and version/release-notes completeness (1.4.1, 1.4.0, 1.3.0, 1.2.0)
   in root `PACKAGE-MANIFEST.md`, companion `PACKAGE-MANIFEST.md`, `README.md`, and `CITATION.cff` (`cff-version: 1.2.0`),
   and ensures zero `__pycache__` or `.pyc` artifacts exist in the repository or manifests.
5. Verifies `Install-Skill.sh` and `Install-Skill.ps1` invoke `Ensure-Maui-DevFlow` strictly inside the `Project` branch,
   support `--skip-devflow` / `-SkipDevFlow`, skip `net9.0-android` projects, pin `0.1.0-preview.14.26531.2` on initial install,
   succeed when Python is absent, and that `Validate-Maui-ObsoleteApis.sh` catches `!= 'Debug'` and `#if !DEBUG` leaks
   both with and without Python.
6. Grades agent responses against deterministic assertions and rejects incomplete/mismatched `--responses` files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ALLOWED_ASSERTION_KEYS = {
    "starts_with",
    "ends_with",
    "ends_with_any",
    "must_contain",
    "must_not_contain",
    "must_match_regex",
    "must_not_match_regex",
    "max_workflow_stages_in_response",
}


def strip_outer_code_fence(text: str) -> str:
    """If a model wrapped its entire response in a single ```...``` fence, unwrap it before checking starts_with/ends_with."""
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            inner = "\n".join(lines[1:-1])
            if "```" not in inner:
                return inner.strip()
    return stripped


def grade_response(assertions: dict[str, object], response_text: str) -> list[str]:
    """Evaluate a single response string against an eval case's assertions. Returns list of failure messages."""
    failures: list[str] = []
    normalized = strip_outer_code_fence(response_text.replace("\r\n", "\n"))

    if not normalized:
        return ["Response is empty."]

    if "starts_with" in assertions:
        expected_start = str(assertions["starts_with"]).strip()
        if not normalized.startswith(expected_start):
            failures.append(f"starts_with failed: expected prefix {expected_start!r}")

    if "ends_with" in assertions:
        expected_end = str(assertions["ends_with"]).strip()
        if not normalized.endswith(expected_end):
            failures.append(f"ends_with failed: expected suffix {expected_end!r}")

    if "ends_with_any" in assertions:
        candidates = [str(item).strip() for item in assertions["ends_with_any"]]
        if not any(normalized.endswith(candidate) for candidate in candidates):
            failures.append(f"ends_with_any failed: response did not end with any of {candidates!r}")

    for substr in assertions.get("must_contain", []):
        if str(substr) not in normalized:
            failures.append(f"must_contain failed: missing {substr!r}")

    for substr in assertions.get("must_not_contain", []):
        if str(substr) in normalized:
            failures.append(f"must_not_contain failed: forbidden substring present {substr!r}")

    for pattern in assertions.get("must_match_regex", []):
        if not re.search(str(pattern), normalized):
            failures.append(f"must_match_regex failed: pattern {pattern!r} did not match")

    for pattern in assertions.get("must_not_match_regex", []):
        if re.search(str(pattern), normalized):
            failures.append(f"must_not_match_regex failed: forbidden pattern {pattern!r} matched")

    if "max_workflow_stages_in_response" in assertions:
        max_stages = int(assertions["max_workflow_stages_in_response"])
        stage_matches = re.findall(r"(?m)^Workflow Stage:\s*[A-Z_]+\s*$", normalized)
        if len(stage_matches) > max_stages:
            failures.append(
                f"max_workflow_stages_in_response failed: found {len(stage_matches)} stages ({stage_matches}), max allowed is {max_stages}"
            )

    return failures


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_all_evals(repo_root: Path) -> tuple[dict[str, dict[str, object]], list[str]]:
    errors: list[str] = []
    all_cases: dict[str, dict[str, object]] = {}

    eval_files = [
        repo_root / "skills/maui-k12-baton-workflow/evals/evals.json",
        repo_root / "companion-skills/maui-step-guide-author/skills/maui-step-guide-author/evals/evals.json",
    ]

    for eval_file in eval_files:
        if not eval_file.is_file():
            errors.append(f"Missing eval file: {eval_file}")
            continue

        try:
            data = json.loads(eval_file.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Invalid JSON in {eval_file}: {exc}")
            continue

        evals = data.get("evals")
        if not isinstance(evals, list) or not evals:
            errors.append(f"{eval_file}: 'evals' must be a non-empty list.")
            continue

        for item in evals:
            eval_id = item.get("id")
            if not eval_id or not isinstance(eval_id, str):
                errors.append(f"{eval_file}: eval entry missing string 'id'.")
                continue
            if eval_id in all_cases:
                errors.append(f"{eval_file}: duplicate eval id '{eval_id}'.")
            all_cases[eval_id] = item

            for req_key in ("prompt", "expected_output", "assertions", "files"):
                if req_key not in item:
                    errors.append(f"{eval_file} [{eval_id}]: missing required key '{req_key}'.")

            assertions = item.get("assertions", {})
            if not isinstance(assertions, dict) or not assertions:
                errors.append(f"{eval_file} [{eval_id}]: 'assertions' must be a non-empty object.")
            else:
                unknown = set(assertions.keys()) - ALLOWED_ASSERTION_KEYS
                if unknown:
                    errors.append(f"{eval_file} [{eval_id}]: unknown assertion keys {sorted(unknown)}.")

            for ref_file in item.get("files", []):
                ref_path = repo_root / ref_file
                if not ref_path.exists():
                    errors.append(f"{eval_file} [{eval_id}]: referenced file does not exist in repo: '{ref_file}'")

    return all_cases, errors


def validate_shared_files(repo_root: Path) -> list[str]:
    errors: list[str] = []
    shared_pairs = [
        (
            "companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/generate_book_pdf.py",
            "project-template/Scripts/Generate-Learning-Book-Pdf.py",
        ),
        (
            "companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/capture_mockup_blocks.py",
            "project-template/Scripts/Capture-Mockup-Blocks.py",
        ),
        (
            "companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/validate_learning_book.py",
            "project-template/Scripts/Validate-Learning-Book.py",
        ),
        (
            "companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/validate_bagrut_compliance.py",
            "project-template/Scripts/Validate-Bagrut-Compliance.py",
        ),
        (
            "companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/generate_architecture_diagrams.py",
            "project-template/Scripts/Generate-Architecture-Diagrams.py",
        ),
        (
            "companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/ensure_maui_devflow.py",
            "project-template/Scripts/Ensure-Maui-DevFlow.py",
        ),
        (
            "companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/ensure_test_project.py",
            "project-template/Scripts/Ensure-Test-Project.py",
        ),
        (
            "companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/validate_tests.py",
            "project-template/Scripts/Validate-Tests.py",
        ),
        (
            "companion-skills/maui-step-guide-author/skills/maui-step-guide-author/scripts/requirements-learning-book.txt",
            "project-template/Scripts/Learning-Book-Requirements.txt",
        ),
    ]

    for src_rel, dst_rel in shared_pairs:
        src_p = repo_root / src_rel
        dst_p = repo_root / dst_rel
        if not src_p.is_file():
            errors.append(f"Missing canonical companion script: {src_rel}")
        elif not dst_p.is_file():
            errors.append(f"Missing project-template copy: {dst_rel}")
        elif sha256_file(src_p) != sha256_file(dst_p):
            errors.append(f"Out-of-sync shared file: {src_rel} != {dst_rel}")

    # Verify AI-And-External-Code-Attribution.md template matches Setup-Skills.ps1 and Setup-Skills.sh
    attr_template = (repo_root / "project-template/Learning/AI-And-External-Code-Attribution.md").read_text(encoding="utf-8").strip()
    setup_ps1 = (repo_root / "project-template/Scripts/Setup-Skills.ps1").read_text(encoding="utf-8")
    setup_sh = (repo_root / "project-template/Scripts/Setup-Skills.sh").read_text(encoding="utf-8")
    if attr_template not in setup_ps1:
        errors.append("project-template/Learning/AI-And-External-Code-Attribution.md does not match embedded template in Setup-Skills.ps1.")
    if attr_template not in setup_sh:
        errors.append("project-template/Learning/AI-And-External-Code-Attribution.md does not match embedded template in Setup-Skills.sh.")

    return errors


def validate_package_manifests(repo_root: Path) -> list[str]:
    errors: list[str] = []
    actual_repo_files: list[str] = []
    for p in sorted(repo_root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(repo_root).as_posix()
        if rel.startswith(".git/"):
            continue
        if "__pycache__" in rel or rel.endswith(".pyc"):
            continue
        actual_repo_files.append(rel)

    manifest_path = repo_root / "PACKAGE-MANIFEST.md"
    if not manifest_path.is_file():
        errors.append("Missing root PACKAGE-MANIFEST.md")
    else:
        mtext = manifest_path.read_text(encoding="utf-8")
        if "__pycache__" in mtext or ".pyc" in mtext:
            errors.append("PACKAGE-MANIFEST.md contains forbidden __pycache__ / .pyc entries.")
        if "Version: 1.5.1" not in mtext:
            errors.append("PACKAGE-MANIFEST.md must declare 'Version: 1.5.1'.")
        for rel_ver in ("1.5.1 Release Notes", "1.5.0 Release Notes", "1.4.1 Release Notes", "1.4.0 Release Notes", "1.3.0 Release Notes", "1.2.0 Release Notes"):
            if rel_ver not in mtext:
                errors.append(f"PACKAGE-MANIFEST.md is missing section '{rel_ver}'.")
        if "Vanilla C# MVVM Policy" not in mtext:
            errors.append("PACKAGE-MANIFEST.md is missing the Vanilla C# MVVM Policy release note.")
        m_inv = re.search(
            r"## Complete Package File Inventory \((?P<count>\d+) Files\)\s*```text\n(?P<block>.*?)```",
            mtext,
            re.DOTALL,
        )
        if not m_inv:
            errors.append("PACKAGE-MANIFEST.md missing '## Complete Package File Inventory (N Files)' text block.")
        else:
            declared_count = int(m_inv.group("count"))
            declared_files = [line.strip() for line in m_inv.group("block").strip().splitlines() if line.strip()]
            if declared_count != len(actual_repo_files):
                errors.append(
                    f"PACKAGE-MANIFEST.md header declares {declared_count} files, but repository has {len(actual_repo_files)} files."
                )
            missing_in_manifest = sorted(set(actual_repo_files) - set(declared_files))
            extra_in_manifest = sorted(set(declared_files) - set(actual_repo_files))
            if missing_in_manifest:
                errors.append(f"PACKAGE-MANIFEST.md is missing {len(missing_in_manifest)} repo file(s): {missing_in_manifest}")
            if extra_in_manifest:
                errors.append(f"PACKAGE-MANIFEST.md lists {len(extra_in_manifest)} non-existent file(s): {extra_in_manifest}")

    # Validate CITATION.cff and README.md versions
    cff_path = repo_root / "CITATION.cff"
    if cff_path.is_file():
        cff_text = cff_path.read_text(encoding="utf-8")
        if "cff-version: 1.2.0" not in cff_text:
            errors.append("CITATION.cff must declare 'cff-version: 1.2.0'.")
        if "version: 1.5.1" not in cff_text:
            errors.append("CITATION.cff must declare 'version: 1.5.1'.")

    readme_path = repo_root / "README.md"
    if readme_path.is_file():
        rtext = readme_path.read_text(encoding="utf-8")
        if "(v1.5.1)" not in rtext:
            errors.append("README.md must reference package version '(v1.5.1)'.")

    comp_root = repo_root / "companion-skills/maui-step-guide-author"
    comp_manifest_path = comp_root / "PACKAGE-MANIFEST.md"
    if comp_manifest_path.is_file():
        actual_comp_files = sorted(
            p.relative_to(comp_root).as_posix()
            for p in comp_root.rglob("*")
            if p.is_file() and "__pycache__" not in p.as_posix() and not p.name.endswith(".pyc")
        )
        ctext = comp_manifest_path.read_text(encoding="utf-8")
        if "Version: 1.5.1" not in ctext:
            errors.append("companion PACKAGE-MANIFEST.md must declare 'Version: 1.5.1'.")
        c_inv = re.search(r"## Included Files\s*```text\n(?P<block>.*?)```", ctext, re.DOTALL)
        if not c_inv:
            errors.append("companion PACKAGE-MANIFEST.md missing '## Included Files' text block.")
        else:
            c_declared = [line.strip() for line in c_inv.group("block").strip().splitlines() if line.strip()]
            c_missing = sorted(set(actual_comp_files) - set(c_declared))
            c_extra = sorted(set(c_declared) - set(actual_comp_files))
            if c_missing:
                errors.append(f"companion PACKAGE-MANIFEST.md missing file(s): {c_missing}")
            if c_extra:
                errors.append(f"companion PACKAGE-MANIFEST.md lists non-existent file(s): {c_extra}")

    return errors


def validate_install_and_compliance_scripts(repo_root: Path) -> list[str]:
    errors: list[str] = []
    sh_text = (repo_root / "scripts/Install-Skill.sh").read_text(encoding="utf-8")
    esac_idx = sh_text.rfind("esac")
    devflow_sh_idx = sh_text.find("Ensure-Maui-DevFlow.sh")
    if devflow_sh_idx == -1 or (esac_idx != -1 and devflow_sh_idx > esac_idx):
        errors.append("scripts/Install-Skill.sh: Ensure-Maui-DevFlow.sh must be invoked inside the Project case before 'esac'.")
    if "--skip-devflow" not in sh_text:
        errors.append("scripts/Install-Skill.sh: missing --skip-devflow opt-out support.")
    if "--skip-cli" not in sh_text:
        errors.append("scripts/Install-Skill.sh: missing --skip-cli opt-out support.")

    ps_text = (repo_root / "scripts/Install-Skill.ps1").read_text(encoding="utf-8")
    codex_idx = ps_text.find('if ($Target -eq "Codex")')
    devflow_ps_idx = ps_text.find("Ensure-Maui-DevFlow.ps1")
    if devflow_ps_idx == -1 or (codex_idx != -1 and devflow_ps_idx > codex_idx):
        errors.append("scripts/Install-Skill.ps1: Ensure-Maui-DevFlow.ps1 must be invoked inside the Project block before its 'return'.")
    if "SkipDevFlow" not in ps_text:
        errors.append("scripts/Install-Skill.ps1: missing -SkipDevFlow opt-out support.")
    if "SkipCli" not in ps_text:
        errors.append("scripts/Install-Skill.ps1: missing -SkipCli opt-out support.")

    ensure_ps1_text = (repo_root / "project-template/Scripts/Ensure-Maui-DevFlow.ps1").read_text(encoding="utf-8")
    if "function Ensure-DevFlowCli" not in ensure_ps1_text or "Microsoft.Maui.Cli" not in ensure_ps1_text:
        errors.append("project-template/Scripts/Ensure-Maui-DevFlow.ps1: missing Ensure-DevFlowCli / Microsoft.Maui.Cli installation.")
    ensure_py_text = (repo_root / "project-template/Scripts/Ensure-Maui-DevFlow.py").read_text(encoding="utf-8")
    if 'shutil.which("maui")' not in ensure_py_text or "Microsoft.Maui.Cli" not in ensure_py_text:
        errors.append("project-template/Scripts/Ensure-Maui-DevFlow.py: missing shutil.which('maui') / Microsoft.Maui.Cli installation.")

    # Run Validate-Bagrut-Compliance.py on project-template and ensure it does NOT print RESULT: PASS
    proc = subprocess.run(
        [sys.executable, str(repo_root / "project-template/Scripts/Validate-Bagrut-Compliance.py"), "--project-root", str(repo_root / "project-template")],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        errors.append(f"Validate-Bagrut-Compliance.py failed on project-template: {proc.stdout} {proc.stderr}")
    elif "RESULT: PASS" in proc.stdout:
        errors.append("Validate-Bagrut-Compliance.py must NEVER print 'RESULT: PASS' as if implementation correctness were proven.")
    elif "DECLARATION_CHECK_OK" not in proc.stdout:
        errors.append("Validate-Bagrut-Compliance.py did not output expected 'RESULT: DECLARATION_CHECK_OK'.")

    # Behavioral regression tests for Ensure-Maui-DevFlow & Validate-Maui-ObsoleteApis
    ensure_py = repo_root / "project-template/Scripts/Ensure-Maui-DevFlow.py"
    ensure_sh = repo_root / "project-template/Scripts/Ensure-Maui-DevFlow.sh"
    obsolete_sh = repo_root / "project-template/Scripts/Validate-Maui-ObsoleteApis.sh"
    obsolete_ps1 = repo_root / "project-template/Scripts/Validate-Maui-ObsoleteApis.ps1"

    with tempfile.TemporaryDirectory(prefix="maui_eval_test_") as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 1. net9.0-android project MUST be skipped by Ensure-Maui-DevFlow
        net9_dir = tmp_path / "net9_app"
        net9_dir.mkdir()
        net9_csproj = net9_dir / "SampleNet9.csproj"
        net9_mp = net9_dir / "MauiProgram.cs"
        net9_csproj.write_text(
            '<Project Sdk="Microsoft.NET.Sdk">\n  <PropertyGroup>\n    <TargetFrameworks>net9.0-android;net9.0-ios</TargetFrameworks>\n    <UseMaui>true</UseMaui>\n  </PropertyGroup>\n</Project>\n',
            encoding="utf-8",
        )
        net9_mp.write_text(
            "using Microsoft.Extensions.Logging;\npublic static class MauiProgram {\n    public static MauiApp CreateMauiApp() {\n        var builder = MauiApp.CreateBuilder();\n        return builder.Build();\n    }\n}\n",
            encoding="utf-8",
        )
        res_net9 = subprocess.run([sys.executable, str(ensure_py), "--project-root", str(net9_dir)], capture_output=True, text=True)
        if res_net9.returncode != 0 or "[SKIP]" not in res_net9.stdout:
            errors.append(f"Ensure-Maui-DevFlow.py did not skip net9.0-android project: {res_net9.stdout}")
        if "Microsoft.Maui.DevFlow" in net9_csproj.read_text(encoding="utf-8") or "AddMauiDevFlowAgent" in net9_mp.read_text(encoding="utf-8"):
            errors.append("Ensure-Maui-DevFlow.py injected DevFlow into a net9.0-android project!")

        # 2. net10.0-android project MUST receive pinned 0.1.0-preview.14.26531.2 on initial install
        net10_dir = tmp_path / "net10_app"
        net10_dir.mkdir()
        net10_csproj = net10_dir / "SampleNet10.csproj"
        net10_mp = net10_dir / "MauiProgram.cs"
        net10_csproj.write_text(
            '<Project Sdk="Microsoft.NET.Sdk">\n  <PropertyGroup>\n    <TargetFrameworks>net10.0-android;net10.0-windows10.0.19041.0</TargetFrameworks>\n    <UseMaui>true</UseMaui>\n  </PropertyGroup>\n</Project>\n',
            encoding="utf-8",
        )
        net10_mp.write_text(
            "using Microsoft.Extensions.Logging;\npublic static class MauiProgram {\n    public static MauiApp CreateMauiApp() {\n        var builder = MauiApp.CreateBuilder();\n        return builder.Build();\n    }\n}\n",
            encoding="utf-8",
        )

        # 3. Leak test project: Condition="'$(Configuration)' != 'Debug'" and #if !DEBUG MUST fail!
        leak_dir = tmp_path / "leak_app"
        leak_dir.mkdir()
        leak_csproj = leak_dir / "LeakApp.csproj"
        leak_mp = leak_dir / "MauiProgram.cs"
        leak_csproj.write_text(
            '<Project Sdk="Microsoft.NET.Sdk">\n  <ItemGroup Condition="\'$(Configuration)\' != \'Debug\'">\n    <PackageReference Include="Microsoft.Maui.DevFlow.Agent" Version="0.1.0-preview.14.26531.2" />\n  </ItemGroup>\n</Project>\n',
            encoding="utf-8",
        )
        leak_mp.write_text(
            "#if !DEBUG\nusing Microsoft.Maui.DevFlow.Agent;\n#endif\npublic static class MauiProgram {\n    public static void Init() {\n#if !DEBUG\n        builder.AddMauiDevFlowAgent();\n#endif\n    }\n}\n",
            encoding="utf-8",
        )

        # 4. SetProperty(ref ...) soft-gate test project (ViewModels vs Views/Controls & Student-Mastery.md)
        sp_dir = tmp_path / "setprop_app"
        (sp_dir / "ViewModels").mkdir(parents=True)
        (sp_dir / "Views").mkdir(parents=True)
        (sp_dir / "Controls").mkdir(parents=True)
        (sp_dir / "Learning").mkdir(parents=True)
        (sp_dir / "ViewModels/ExampleViewModel.cs").write_text(
            "public class ExampleViewModel {\n    private string _title = \"\";\n    public string Title {\n        get => _title;\n        set => SetProperty(ref _title, value);\n    }\n}\n",
            encoding="utf-8",
        )
        (sp_dir / "Views/CustomView.cs").write_text(
            "public class CustomView {\n    private string _label = \"\";\n    public void Update(string v) => SetProperty(ref _label, v);\n}\n",
            encoding="utf-8",
        )
        (sp_dir / "Controls/BadgeControl.cs").write_text(
            "public class BadgeControl {\n    private int _count;\n    public void SetCount(int c) => SetProperty(ref _count, c);\n}\n",
            encoding="utf-8",
        )
        default_mastery = (repo_root / "project-template/Learning/Student-Mastery.md").read_text(encoding="utf-8")
        (sp_dir / "Learning/Student-Mastery.md").write_text(default_mastery, encoding="utf-8")

        if os.name != "nt" and Path("/bin/bash").exists():
            # Create a bin directory without python/python3 to test Python-less Bash execution
            no_py_bin = tmp_path / "no_py_bin"
            no_py_bin.mkdir()
            for tool in ("bash", "sh", "awk", "grep", "sed", "find", "sort", "tr", "dirname", "basename", "mkdir", "cp", "mv", "rm", "cat", "cmp", "chmod", "head", "wc", "id"):
                for sys_dir in ("/usr/bin", "/bin"):
                    cand = Path(sys_dir) / tool
                    if cand.exists():
                        (no_py_bin / tool).symlink_to(cand)
                        break

            no_py_env = {**os.environ, "PATH": str(no_py_bin), "MAUI_NO_PYTHON_INSTALL": "1", "MAUI_SKIP_DEVFLOW_CLI": "1"}
            res_nopy_inject = subprocess.run(["/bin/bash", str(ensure_sh), str(net10_dir), "--skip-cli"], env=no_py_env, capture_output=True, text=True)
            if res_nopy_inject.returncode != 0:
                errors.append(f"Ensure-Maui-DevFlow.sh failed when Python was absent: {res_nopy_inject.stdout} {res_nopy_inject.stderr}")
            if 'Version="0.1.0-preview.14.26531.2"' not in net10_csproj.read_text(encoding="utf-8"):
                errors.append("Ensure-Maui-DevFlow.sh (without Python) did not inject pinned 0.1.0-preview.14.26531.2 into net10.0 .csproj.")
            if "AddMauiDevFlowAgent()" not in net10_mp.read_text(encoding="utf-8"):
                errors.append("Ensure-Maui-DevFlow.sh (without Python) did not inject AddMauiDevFlowAgent() into MauiProgram.cs.")

            res_valid_py = subprocess.run(["/bin/bash", str(obsolete_sh), str(net10_dir)], capture_output=True, text=True)
            if res_valid_py.returncode != 0:
                errors.append(f"Validate-Maui-ObsoleteApis.sh failed on valid net10 Debug-only DevFlow project: {res_valid_py.stdout}")
            res_valid_nopy = subprocess.run(["/bin/bash", str(obsolete_sh), str(net10_dir)], env=no_py_env, capture_output=True, text=True)
            if res_valid_nopy.returncode != 0:
                errors.append(f"Validate-Maui-ObsoleteApis.sh (without Python) failed on valid net10 project: {res_valid_nopy.stdout}")

            res_leak_py = subprocess.run(["/bin/bash", str(obsolete_sh), str(leak_dir)], capture_output=True, text=True)
            if res_leak_py.returncode == 0 or "[RELEASE LEAK]" not in res_leak_py.stdout:
                errors.append("Validate-Maui-ObsoleteApis.sh (with Python) did NOT catch != 'Debug' and #if !DEBUG bypasses!")

            res_leak_nopy = subprocess.run(["/bin/bash", str(obsolete_sh), str(leak_dir)], env=no_py_env, capture_output=True, text=True)
            if res_leak_nopy.returncode == 0 or "[RELEASE LEAK]" not in res_leak_nopy.stdout:
                errors.append("Validate-Maui-ObsoleteApis.sh (without Python) did NOT catch != 'Debug' and #if !DEBUG bypasses!")

            res_sp_warn = subprocess.run(["/bin/bash", str(obsolete_sh), str(sp_dir)], capture_output=True, text=True)
            if res_sp_warn.returncode != 0:
                errors.append(f"Validate-Maui-ObsoleteApis.sh failed (non-zero exit) on SetProperty pedagogical warning: {res_sp_warn.stdout}")
            if "[PEDAGOGICAL WARNING] ViewModels/ExampleViewModel.cs:5 - SetProperty(ref...) detected." not in res_sp_warn.stdout:
                errors.append(f"Validate-Maui-ObsoleteApis.sh did not emit expected SetProperty pedagogical warning for ViewModel: {res_sp_warn.stdout}")
            if "CustomView.cs" in res_sp_warn.stdout or "BadgeControl.cs" in res_sp_warn.stdout:
                errors.append("Validate-Maui-ObsoleteApis.sh did not skip Views/ and Controls/ for SetProperty check!")
        else:
            # Windows / cross-platform Python + PowerShell verification
            res_py_inject = subprocess.run([sys.executable, str(ensure_py), "--project-root", str(net10_dir), "--skip-cli"], capture_output=True, text=True)
            if res_py_inject.returncode != 0:
                errors.append(f"Ensure-Maui-DevFlow.py failed on net10 project: {res_py_inject.stdout} {res_py_inject.stderr}")
            if 'Version="0.1.0-preview.14.26531.2"' not in net10_csproj.read_text(encoding="utf-8"):
                errors.append("Ensure-Maui-DevFlow.py did not inject pinned 0.1.0-preview.14.26531.2 into net10.0 .csproj.")
            if "AddMauiDevFlowAgent()" not in net10_mp.read_text(encoding="utf-8"):
                errors.append("Ensure-Maui-DevFlow.py did not inject AddMauiDevFlowAgent() into MauiProgram.cs.")

            # Verify Validate-Learning-Book.py catches missing screen image and missing PDF
            vlb_py = repo_root / "project-template/Scripts/Validate-Learning-Book.py"
            book_test_dir = tmp_path / "book_test_app"
            (book_test_dir / "Views").mkdir(parents=True)
            (book_test_dir / "Learning/Images").mkdir(parents=True)
            (book_test_dir / "Views/DashboardPage.xaml").write_text("<ContentPage />", encoding="utf-8")
            res_vlb = subprocess.run(
                [
                    sys.executable,
                    str(vlb_py),
                    "--html",
                    str(book_test_dir / "Learning/MAUI-Learning-Book.html"),
                    "--pdf",
                    str(book_test_dir / "Learning/MAUI-Learning-Book.pdf"),
                    "--report",
                    str(book_test_dir / "Learning/MAUI-Learning-Book.validation.json"),
                    "--project-root",
                    str(book_test_dir),
                ],
                capture_output=True,
                text=True,
            )
            if res_vlb.returncode == 0 or "DashboardPage" not in (res_vlb.stdout + res_vlb.stderr):
                errors.append(f"Validate-Learning-Book.py did not fail on missing screen image for DashboardPage: {res_vlb.stdout} {res_vlb.stderr}")

            # 5. Verify Ensure-Test-Project.py & Validate-Tests.py (TFM injection, testManagementMode override, includeTests=false)
            ensure_test_py = repo_root / "project-template/Scripts/Ensure-Test-Project.py"
            val_test_py = repo_root / "project-template/Scripts/Validate-Tests.py"
            t_app_dir = tmp_path / "test_prov_app"
            (t_app_dir / ".agents").mkdir(parents=True)
            (t_app_dir / "LearnStylesMaui").mkdir(parents=True)
            (t_app_dir / "LearnStylesMaui/LearnStylesMaui.csproj").write_text(
                '<Project Sdk="Microsoft.NET.Sdk">\n  <PropertyGroup>\n    <TargetFrameworks>net10.0-android;net10.0-windows10.0.19041.0</TargetFrameworks>\n    <OutputType>Exe</OutputType>\n    <UseMaui>true</UseMaui>\n  </PropertyGroup>\n</Project>\n',
                encoding="utf-8",
            )
            # In MAXIMIZE CODE GENERATED (studentCapabilityMode=false), even if testManagementMode="student", effective writer must be "agent"
            (t_app_dir / ".agents/MAUI-Agent-Mode.json").write_text(
                '{"studentCapabilityMode": false, "includeTests": true, "testManagementMode": "student"}',
                encoding="utf-8",
            )
            res_etp = subprocess.run([sys.executable, str(ensure_test_py), "--project-root", str(t_app_dir), "--offline"], capture_output=True, text=True)
            if res_etp.returncode != 0 or "effective writer: agent" not in res_etp.stdout:
                errors.append(f"Ensure-Test-Project.py failed or did not override testManagementMode to 'agent' when studentCapabilityMode=false: {res_etp.stdout}")
            updated_maui_csproj = (t_app_dir / "LearnStylesMaui/LearnStylesMaui.csproj").read_text(encoding="utf-8")
            if "<TargetFrameworks>net10.0;net10.0-android" not in updated_maui_csproj:
                errors.append(f"Ensure-Test-Project.py did not add plain net10.0 to <TargetFrameworks>: {updated_maui_csproj}")
            test_csproj_file = t_app_dir / "LearnStylesMaui.Tests/LearnStylesMaui.Tests.csproj"
            if not test_csproj_file.is_file():
                errors.append("Ensure-Test-Project.py did not create LearnStylesMaui.Tests.csproj!")
            else:
                test_csproj_txt = test_csproj_file.read_text(encoding="utf-8")
                if 'Include="xunit.v3"' not in test_csproj_txt or "<OutputType>Exe</OutputType>" not in test_csproj_txt:
                    errors.append(f"Ensure-Test-Project.py did not provision xunit.v3 with OutputType=Exe: {test_csproj_txt}")
            if not (t_app_dir / "Learning/Test-Documentation.md").is_file():
                errors.append("Ensure-Test-Project.py did not initialize Learning/Test-Documentation.md!")

            res_vt_pass = subprocess.run([sys.executable, str(val_test_py), "--project-root", str(t_app_dir), "--skip-dotnet-run"], capture_output=True, text=True)
            if res_vt_pass.returncode != 0 or "effective writer: agent" not in res_vt_pass.stdout:
                errors.append(f"Validate-Tests.py failed on valid provisioned test project: {res_vt_pass.stdout} {res_vt_pass.stderr}")

            # When includeTests=false, Validate-Tests.py must ignore testManagementMode and pass even if *.Tests.csproj is deleted
            shutil.rmtree(t_app_dir / "LearnStylesMaui.Tests")
            (t_app_dir / ".agents/MAUI-Agent-Mode.json").write_text(
                '{"studentCapabilityMode": true, "includeTests": false, "testManagementMode": "student"}',
                encoding="utf-8",
            )
            res_vt_disabled = subprocess.run([sys.executable, str(val_test_py), "--project-root", str(t_app_dir)], capture_output=True, text=True)
            if res_vt_disabled.returncode != 0 or "TESTS DISABLED" not in res_vt_disabled.stdout:
                errors.append(f"Validate-Tests.py did not skip when includeTests=false: {res_vt_disabled.stdout}")

            pwsh_exe = shutil.which("powershell.exe") or shutil.which("pwsh")
            if pwsh_exe:
                ensure_ps1 = repo_root / "project-template/Scripts/Ensure-Maui-DevFlow.ps1"
                res_devflow_ps = subprocess.run(
                    [pwsh_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ensure_ps1), "-ProjectRoot", str(net10_dir), "-SkipCli", "-Offline"],
                    capture_output=True,
                    text=True,
                )
                if res_devflow_ps.returncode != 0:
                    errors.append(f"Ensure-Maui-DevFlow.ps1 failed with PowerShell flags: {res_devflow_ps.stdout} {res_devflow_ps.stderr}")

                res_devflow_posix_ps = subprocess.run(
                    [pwsh_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ensure_ps1), "--project-root", str(net10_dir), "--skip-cli", "--offline", "--dry-run"],
                    capture_output=True,
                    text=True,
                )
                if res_devflow_posix_ps.returncode != 0:
                    errors.append(f"Ensure-Maui-DevFlow.ps1 failed with POSIX flags (--project-root / --skip-cli): {res_devflow_posix_ps.stdout} {res_devflow_posix_ps.stderr}")

                ensure_test_ps1 = repo_root / "project-template/Scripts/Ensure-Test-Project.ps1"
                val_test_ps1 = repo_root / "project-template/Scripts/Validate-Tests.ps1"
                res_etp_ps = subprocess.run(
                    [pwsh_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ensure_test_ps1), "-ProjectRoot", str(net10_dir), "-Offline"],
                    capture_output=True,
                    text=True,
                )
                if res_etp_ps.returncode != 0:
                    errors.append(f"Ensure-Test-Project.ps1 failed via PowerShell: {res_etp_ps.stdout} {res_etp_ps.stderr}")

                res_vt_ps = subprocess.run(
                    [pwsh_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(val_test_ps1), "-ProjectRoot", str(net10_dir), "-SkipDotnetRun"],
                    capture_output=True,
                    text=True,
                )
                if res_vt_ps.returncode != 0:
                    errors.append(f"Validate-Tests.ps1 failed via PowerShell (WindowsApps alias check): {res_vt_ps.stdout} {res_vt_ps.stderr}")

                res_valid_ps = subprocess.run(
                    [pwsh_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(obsolete_ps1), "-ProjectRoot", str(net10_dir)],
                    capture_output=True,
                    text=True,
                )
                if res_valid_ps.returncode != 0:
                    errors.append(f"Validate-Maui-ObsoleteApis.ps1 failed on valid net10 project: {res_valid_ps.stdout}")

                res_leak_ps = subprocess.run(
                    [pwsh_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(obsolete_ps1), "-ProjectRoot", str(leak_dir)],
                    capture_output=True,
                    text=True,
                )
                if res_leak_ps.returncode == 0 or "[RELEASE LEAK]" not in res_leak_ps.stdout:
                    errors.append("Validate-Maui-ObsoleteApis.ps1 did NOT catch != 'Debug' and #if !DEBUG bypasses!")

                # Verify SetProperty(ref...) soft-gate in PowerShell: unmastered -> warning + exit 0; Views/Controls ignored
                res_sp_ps = subprocess.run(
                    [pwsh_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(obsolete_ps1), "-ProjectRoot", str(sp_dir)],
                    capture_output=True,
                    text=True,
                )
                if res_sp_ps.returncode != 0:
                    errors.append(f"Validate-Maui-ObsoleteApis.ps1 returned non-zero on SetProperty pedagogical warning: {res_sp_ps.stdout}")
                if "[PEDAGOGICAL WARNING] ViewModels/ExampleViewModel.cs:5 - SetProperty(ref...) detected." not in res_sp_ps.stdout:
                    errors.append(f"Validate-Maui-ObsoleteApis.ps1 did not emit expected SetProperty warning: {res_sp_ps.stdout}")
                if "CustomView.cs" in res_sp_ps.stdout or "BadgeControl.cs" in res_sp_ps.stdout:
                    errors.append("Validate-Maui-ObsoleteApis.ps1 did not skip Views/ and Controls/ for SetProperty check!")

                # Now mark INotifyPropertyChanged as Routine eligibility: Yes in Student-Mastery.md and verify warning is silenced
                mastered_text = default_mastery.replace(
                    "### INotifyPropertyChanged\n- Level: Not introduced\n- Theory evidence: None\n- Applied coding evidence: None\n- Evidence source: None\n- Routine eligibility: No",
                    "### INotifyPropertyChanged\n- Level: Can work independently\n- Theory evidence: Explained ref and SetProperty\n- Applied coding evidence: Implemented ViewModel properties\n- Evidence source: ViewModels/ExampleViewModel.cs\n- Routine eligibility: Yes",
                )
                (sp_dir / "Learning/Student-Mastery.md").write_text(mastered_text, encoding="utf-8")
                res_sp_mastered_ps = subprocess.run(
                    [pwsh_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(obsolete_ps1), "-ProjectRoot", str(sp_dir)],
                    capture_output=True,
                    text=True,
                )
                if res_sp_mastered_ps.returncode != 0 or "[PEDAGOGICAL WARNING]" in res_sp_mastered_ps.stdout:
                    errors.append(f"Validate-Maui-ObsoleteApis.ps1 did not pass silently when SetProperty/ref is mastered: {res_sp_mastered_ps.stdout}")

    return errors


def grade_response_file(all_cases: dict[str, dict[str, object]], resp_path: Path, allow_subset: bool) -> int:
    if not resp_path.is_file():
        print(f"Error: responses file not found: {resp_path}", file=sys.stderr)
        return 2

    responses = json.loads(resp_path.read_text(encoding="utf-8"))
    if not isinstance(responses, dict) or not responses:
        print(f"Error: {resp_path} must be a non-empty JSON object mapping eval_id -> response text.", file=sys.stderr)
        return 2

    unknown_ids = sorted(set(responses.keys()) - set(all_cases.keys()))
    if unknown_ids:
        print(f"FAIL: Unknown eval IDs in {resp_path}: {unknown_ids}", file=sys.stderr)
        return 2

    missing_ids = sorted(set(all_cases.keys()) - set(responses.keys()))
    if missing_ids and not allow_subset:
        print(f"FAIL: Missing {len(missing_ids)} eval ID(s) in {resp_path}: {missing_ids}", file=sys.stderr)
        return 2

    total = 0
    failed = 0
    for eid, item in all_cases.items():
        if eid not in responses:
            continue
        total += 1
        item_failures = grade_response(item["assertions"], str(responses[eid]))
        if item_failures:
            failed += 1
            print(f"[FAIL] {eid}:", file=sys.stderr)
            for fmsg in item_failures:
                print(f"    {fmsg}", file=sys.stderr)
        else:
            print(f"[PASS] {eid}")

    if total == 0:
        print("FAIL: 0 responses graded.", file=sys.stderr)
        return 2

    if failed:
        print(f"Graded {total} responses: {failed} failed.", file=sys.stderr)
        return 2

    print(f"Graded {total} responses: all passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and grade MAUI K12 Baton Workflow evals.")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parent.parent), help="Repository root path")
    parser.add_argument(
        "--responses",
        help="Optional JSON file mapping eval_id -> agent response text. Defaults to scripts/golden-eval-responses.json.",
    )
    parser.add_argument(
        "--allow-subset",
        action="store_true",
        help="Allow --responses to contain only a subset of eval IDs (still fails if 0 match or unknown IDs exist).",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    all_cases, errors = load_all_evals(repo_root)
    errors.extend(validate_shared_files(repo_root))
    errors.extend(validate_package_manifests(repo_root))
    errors.extend(validate_install_and_compliance_scripts(repo_root))

    # Negative regression self-tests
    if "explaining-agent-code-is-not-practice" in all_cases:
        bad_reply = "Mode: MAXIMIZE STUDENT CAPABILITY\nRoutine eligibility: Yes\nWorkflow Stage: OWNERSHIP_NEGOTIATOR\nStatus: OWNERSHIP_SELECTION_PENDING"
        if not grade_response(all_cases["explaining-agent-code-is-not-practice"]["assertions"], bad_reply):
            errors.append("Self-test failed: grader did not catch forbidden 'Routine eligibility: Yes' line.")

    if "new-project-build-along" in all_cases:
        if not grade_response(all_cases["new-project-build-along"]["assertions"], ""):
            errors.append("Self-test failed: grader did not reject an empty response.")

    if errors:
        print("FAIL: Package & eval validation found issues:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"PASS: Validated {len(all_cases)} eval definitions, exact manifest inventories, installer branches, shared script hashes, and negative self-tests.")

    resp_path = Path(args.responses).resolve() if args.responses else (repo_root / "scripts/golden-eval-responses.json")
    return grade_response_file(all_cases, resp_path, args.allow_subset)


if __name__ == "__main__":
    raise SystemExit(main())
