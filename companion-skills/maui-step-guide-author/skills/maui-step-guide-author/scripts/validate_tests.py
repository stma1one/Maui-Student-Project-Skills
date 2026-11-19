#!/usr/bin/env python3
"""
Validate-Tests.py
-----------------
Programmatic validation gate for xUnit tests in .NET MAUI student projects.

Rules:
1. Reads `.agents/MAUI-Agent-Mode.json`:
   - If `"includeTests": false`, ignores `"testManagementMode"`, prints a skip notice, and exits 0.
   - If `"studentCapabilityMode": false` (MAXIMIZE CODE GENERATED) and `"includeTests": true`, the effective test writer
     is ALWAYS `"agent"` (regardless of `"testManagementMode"`), and `Learning/Test-Documentation.md` MUST exist.
2. Verifies that a `*.Tests.csproj` file exists in the project directory.
3. Runs `dotnet test` against the `*.Tests.csproj` project and verifies:
   - Exit code == 0
   - Failed == 0
   - Passed >= 1 (rejects 0-test runs)
4. Exits 1 if any requirement is not met.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys

EXCLUDED_DIRS = {
    ".git",
    ".vs",
    ".idea",
    "bin",
    "obj",
    "node_modules",
    ".agents",
    ".claude",
    "companion-skills",
    "skills",
    "project-template",
}


def is_excluded(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        rel_parts = path.parts
    return any(part in EXCLUDED_DIRS for part in rel_parts)


def read_agent_mode(root: pathlib.Path) -> tuple[bool, bool, str, str]:
    """Return (student_capability_mode, include_tests, configured_writer, effective_writer)."""
    mode_file = root / ".agents/MAUI-Agent-Mode.json"
    student_mode = True
    include_tests = True
    configured_writer = "combined"

    if mode_file.is_file():
        try:
            data = json.loads(mode_file.read_text(encoding="utf-8", errors="ignore"))
            if isinstance(data, dict):
                if "studentCapabilityMode" in data:
                    student_mode = bool(data["studentCapabilityMode"])
                if "includeTests" in data:
                    include_tests = bool(data["includeTests"])
                if "testManagementMode" in data and isinstance(data["testManagementMode"], str):
                    cand = data["testManagementMode"].strip().lower()
                    if cand in {"agent", "student", "combined"}:
                        configured_writer = cand
        except Exception:
            pass

    if not include_tests:
        effective_writer = "ignored"
    elif not student_mode:
        effective_writer = "agent"
    else:
        effective_writer = configured_writer

    return student_mode, include_tests, configured_writer, effective_writer


def find_test_csproj_files(root: pathlib.Path) -> list[pathlib.Path]:
    results: list[pathlib.Path] = []
    for csproj in sorted(root.rglob("*.csproj")):
        if is_excluded(csproj, root):
            continue
        name_low = csproj.name.lower()
        if name_low.endswith(".tests.csproj") or name_low.endswith("tests.csproj") or name_low.endswith("test.csproj"):
            results.append(csproj)
            continue
        try:
            text = csproj.read_text(encoding="utf-8", errors="ignore")
            if "<IsTestProject>true</IsTestProject>" in text or 'Include="xunit"' in text:
                results.append(csproj)
        except OSError:
            pass
    return results


def parse_dotnet_test_counts(output: str) -> tuple[int, int]:
    """Extract (passed_count, failed_count) from dotnet test stdout/stderr across locales."""
    passed = 0
    failed = 0

    for m in re.finditer(r"Passed!\s*-\s*Failed:\s*(\d+),\s*Passed:\s*(\d+)", output, re.IGNORECASE):
        failed += int(m.group(1))
        passed += int(m.group(2))

    for m in re.finditer(r"Failed!\s*-\s*Failed:\s*(\d+),\s*Passed:\s*(\d+)", output, re.IGNORECASE):
        failed += int(m.group(1))
        passed += int(m.group(2))

    if passed == 0 and failed == 0:
        m_p = re.findall(r"(?:Passed|עברו בהצלחה)\s*:\s*(\d+)", output, re.IGNORECASE)
        m_f = re.findall(r"(?:Failed|נכשלו)\s*:\s*(\d+)", output, re.IGNORECASE)
        if m_p:
            passed = sum(int(x) for x in m_p)
        if m_f:
            failed = sum(int(x) for x in m_f)

    return passed, failed


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate xUnit test project, test execution, and Test-Documentation.md.")
    parser.add_argument("--project-root", default=".", help="Path to the .NET MAUI project root directory.")
    parser.add_argument("--skip-dotnet-run", action="store_true", help="Validate project and test files statically without invoking dotnet test.")
    args = parser.parse_args()

    root = pathlib.Path(args.project_root).resolve()
    student_mode, include_tests, configured_writer, effective_writer = read_agent_mode(root)

    if not include_tests:
        print("[SKIP] includeTests=false in .agents/MAUI-Agent-Mode.json — unit tests are disabled (testManagementMode ignored).")
        print("RESULT: PASS (TESTS DISABLED)")
        return 0

    mode_label = "MAXIMIZE STUDENT CAPABILITY" if student_mode else "MAXIMIZE CODE GENERATED"
    print(f"[INFO] Validating xUnit tests (Mode: {mode_label}, includeTests: true, testManagementMode: {configured_writer}, effective writer: {effective_writer})")

    test_csprojs = find_test_csproj_files(root)
    if not test_csprojs:
        print(f"[FAIL] No *.Tests.csproj found under {root}. Run Ensure-Test-Project to provision <AppName>.Tests.", file=sys.stderr)
        print("RESULT: CHECK REQUIRED", file=sys.stderr)
        return 1

    # Verify Learning/Test-Documentation.md exists
    test_doc = root / "Learning/Test-Documentation.md"
    if not test_doc.is_file() or test_doc.stat().st_size == 0:
        print(
            f"[FAIL] Missing or empty '{test_doc}'. Document all tested logic components and Arrange-Act-Assert cases in Learning/Test-Documentation.md.",
            file=sys.stderr,
        )
        print("RESULT: CHECK REQUIRED", file=sys.stderr)
        return 1

    # Verify at least one [Fact] or [Theory] exists in the test project
    fact_count = 0
    for t_csproj in test_csprojs:
        for cs_file in sorted(t_csproj.parent.rglob("*.cs")):
            if "/bin/" in cs_file.as_posix() or "/obj/" in cs_file.as_posix():
                continue
            txt = cs_file.read_text(encoding="utf-8", errors="ignore")
            fact_count += len(re.findall(r"\[\s*(?:Fact|Theory)\b", txt))

    if fact_count < 1:
        print("[FAIL] No [Fact] or [Theory] test methods found in *.Tests project (Passed >= 1 required).", file=sys.stderr)
        print("RESULT: CHECK REQUIRED", file=sys.stderr)
        return 1

    if args.skip_dotnet_run:
        print(f"RESULT: PASS (Static check: {len(test_csprojs)} test project(s), {fact_count} test method(s), effective writer: {effective_writer})")
        return 0

    if shutil.which("dotnet") is None:
        print("[FAIL] 'dotnet' CLI is not available in PATH to execute dotnet test.", file=sys.stderr)
        return 1

    total_passed = 0
    total_failed = 0
    for t_csproj in test_csprojs:
        print(f"[INFO] Running: dotnet test {t_csproj} --verbosity normal")
        proc = subprocess.run(
            ["dotnet", "test", str(t_csproj), "--verbosity", "normal"],
            capture_output=True,
            text=True,
            check=False,
        )
        combined_out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        passed, failed = parse_dotnet_test_counts(combined_out)
        total_passed += passed
        total_failed += failed

        if proc.returncode != 0 or failed > 0:
            print(combined_out, file=sys.stderr)
            print(f"[FAIL] dotnet test failed for {t_csproj.name} (Passed: {passed}, Failed: {failed}, ExitCode: {proc.returncode}).", file=sys.stderr)
            print("RESULT: CHECK REQUIRED", file=sys.stderr)
            return 1

    if total_passed < 1:
        print(f"[FAIL] dotnet test completed with Passed == {total_passed} (Passed >= 1 is strictly required).", file=sys.stderr)
        print("RESULT: CHECK REQUIRED", file=sys.stderr)
        return 1

    print(f"RESULT: PASS (Passed: {total_passed}, Failed: {total_failed}, Effective Writer: {effective_writer})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
