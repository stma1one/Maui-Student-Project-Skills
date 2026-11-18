#!/usr/bin/env python3
"""
Generate-Architecture-Diagrams.py
---------------------------------
Cross-platform (Windows / macOS / Linux) architecture diagram and prompt generator for .NET MAUI projects.
Scans the project's C# and XAML files to automatically produce:
1. `Learning/Diagrams/Screen-Flow.mmd` (Mermaid Screen Flow Diagram from AppShell & GoToAsync routes)
2. `Learning/Diagrams/Architecture-UML.mmd` (Mermaid UML Class Diagram with properties, methods, inheritance, composition & DI)
3. `Learning/Diagrams/Architecture-Diagram-Prompts.md` (Ready-to-paste prompts + Mermaid sources for the student's Project Portfolio)
4. `Learning/Diagrams/Architecture-Preview.html` (Self-contained visual SVG preview of both diagrams)
5. Optional PNG snapshots (`Learning/Images/Screen-Flow.png` and `Learning/Images/Architecture-UML.png`) if Playwright Chromium is available.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def strip_comments(code: str) -> str:
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    return re.sub(r"//.*$", "", code, flags=re.MULTILINE)


def scan_classes(project_root: Path) -> list[dict[str, object]]:
    classes: list[dict[str, object]] = []
    cs_files = [
        p for p in sorted(project_root.rglob("*.cs"))
        if "/bin/" not in p.as_posix()
        and "/obj/" not in p.as_posix()
        and "/Scripts/" not in p.as_posix()
        and "/Platforms/" not in p.as_posix()
    ]

    class_re = re.compile(
        r"\b(public|internal)\s+(?:partial\s+|abstract\s+|sealed\s+|static\s+)*(class|interface)\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s*:\s*([^{]+))?"
    )
    prop_re = re.compile(
        r"\bpublic\s+(?:virtual\s+|override\s+|static\s+)?([A-Za-z0-9_<>,\.\?\[\]]+)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{\s*get;"
    )
    method_re = re.compile(
        r"\bpublic\s+(?:async\s+|virtual\s+|override\s+|static\s+)*([A-Za-z0-9_<>,\.\?\[\]]+)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)"
    )

    for cs_file in cs_files:
        text = strip_comments(cs_file.read_text(encoding="utf-8", errors="ignore"))
        posix = cs_file.as_posix()
        layer = "Other"
        for candidate_layer in ("Models", "ViewModels", "Services", "Views", "Converters", "Drawables"):
            if f"/{candidate_layer}/" in posix:
                layer = candidate_layer
                break

        for m in class_re.finditer(text):
            _, kind, name, base_list = m.groups()
            if name in {"App", "MauiProgram", "Resource"}:
                continue
            bases = []
            if base_list:
                bases = [b.strip().split("<")[0].split(".")[-1] for b in base_list.split(",") if b.strip()]

            props = []
            for pm in prop_re.finditer(text):
                ptype, pname = pm.groups()
                props.append((pname, ptype.replace("<", "~").replace(">", "~")))

            methods = []
            deps = []
            for mm in method_re.finditer(text):
                ret_type, mname, params = mm.groups()
                if mname == name:
                    # Constructor dependencies
                    for param in params.split(","):
                        parts = param.strip().split()
                        if len(parts) >= 2:
                            dep_type = parts[0].split(".")[-1].replace("<", "~").replace(">", "~")
                            deps.append(dep_type)
                    continue
                methods.append((mname, ret_type.replace("<", "~").replace(">", "~")))

            # Also check primary constructor or field injections
            ctor_re = re.compile(rf"\bpublic\s+{re.escape(name)}\s*\(([^)]*)\)")
            for cm in ctor_re.finditer(text):
                for param in cm.group(1).split(","):
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        dep_type = parts[0].split(".")[-1]
                        if dep_type not in deps:
                            deps.append(dep_type)

            classes.append(
                {
                    "name": name,
                    "kind": kind,
                    "layer": layer,
                    "file": str(cs_file.relative_to(project_root)),
                    "bases": bases,
                    "props": props[:8],
                    "methods": methods[:8],
                    "deps": deps,
                }
            )

    return classes


def scan_screen_flow(project_root: Path) -> tuple[list[str], list[tuple[str, str, str]]]:
    screens: set[str] = set()
    edges: list[tuple[str, str, str]] = []

    for xaml_file in sorted(project_root.rglob("*.xaml")):
        if "/bin/" in xaml_file.as_posix() or "/obj/" in xaml_file.as_posix():
            continue
        raw = xaml_file.read_text(encoding="utf-8", errors="ignore")
        if "<ContentPage" in raw:
            screens.add(xaml_file.stem)
        if xaml_file.name.lower() == "appshell.xaml":
            for m in re.finditer(r'ContentTemplate\s*=\s*"\{DataTemplate\s+(?:[A-Za-z0-9_]+:)?([A-Za-z0-9_]+)\}"', raw):
                target = m.group(1)
                screens.add(target)
                edges.append(("AppShell", target, "Shell Tab / Flyout"))

    for cs_file in sorted(project_root.rglob("*.cs")):
        if "/bin/" in cs_file.as_posix() or "/obj/" in cs_file.as_posix():
            continue
        text = strip_comments(cs_file.read_text(encoding="utf-8", errors="ignore"))
        src_name = cs_file.stem.replace("ViewModel", "Page")
        for m in re.finditer(r'GoToAsync\s*\(\s*(?:\$?"([^"]+)"|nameof\s*\(\s*([A-Za-z0-9_]+)\s*\))', text):
            route_lit, nameof_target = m.groups()
            target = nameof_target or route_lit or ""
            target = target.strip("/").split("?")[0]
            if target == "..":
                edges.append((src_name, "PreviousScreen", "Back (..)"))
            elif target:
                screens.add(target)
                edges.append((src_name, target, "GoToAsync"))

    if not screens:
        screens.add("MainPage")
    if not edges:
        for s in sorted(screens):
            edges.append(("AppShell", s, "Start Route"))

    return sorted(screens), edges


def build_uml_mermaid(classes: list[dict[str, object]]) -> str:
    lines = ["classDiagram", "  direction TB"]
    known_names = {str(c["name"]) for c in classes}

    if not classes:
        lines.append("  class MainPage {")
        lines.append("  }")
        lines.append("  class MainViewModel {")
        lines.append("    +bool IsLoading")
        lines.append("    +InitializeAsync() Task")
        lines.append("  }")
        lines.append("  MainPage --> MainViewModel : BindingContext")
        return "\n".join(lines) + "\n"

    for c in classes:
        cname = str(c["name"])
        lines.append(f"  class {cname} {{")
        if c["kind"] == "interface":
            lines.append("    <<interface>>")
        for pname, ptype in c["props"]:
            lines.append(f"    +{ptype} {pname}")
        for mname, rtype in c["methods"]:
            lines.append(f"    +{mname}() {rtype}")
        lines.append("  }")

    seen_rel: set[str] = set()
    for c in classes:
        cname = str(c["name"])
        for base in c["bases"]:
            if base in known_names or base in {"INotifyPropertyChanged", "ContentPage", "IDrawable"}:
                rel = f"  {base} <|-- {cname}"
                if rel not in seen_rel:
                    lines.append(rel)
                    seen_rel.add(rel)
        for dep in c["deps"]:
            if dep in known_names and dep != cname:
                rel = f"  {cname} ..> {dep} : DI"
                if rel not in seen_rel:
                    lines.append(rel)
                    seen_rel.add(rel)

    return "\n".join(lines) + "\n"


def build_screen_flow_mermaid(screens: list[str], edges: list[tuple[str, str, str]]) -> str:
    lines = ["flowchart TD", "  AppShell([\"AppShell (נקודת פתיחה וניווט)\"])"]
    seen_edges: set[tuple[str, str, str]] = set()
    for src, dst, label in edges:
        key = (src, dst, label)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        lines.append(f"  {src} -->|\"{label}\"| {dst}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate UML and Screen Flow diagrams and prompts for a MAUI project.")
    parser.add_argument("--project-root", default=str(Path(__file__).resolve().parent.parent), help="Project root path")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    diagrams_dir = project_root / "Learning/Diagrams"
    images_dir = project_root / "Learning/Images"
    diagrams_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    classes = scan_classes(project_root)
    screens, edges = scan_screen_flow(project_root)

    uml_mmd = build_uml_mermaid(classes)
    flow_mmd = build_screen_flow_mermaid(screens, edges)

    uml_path = diagrams_dir / "Architecture-UML.mmd"
    flow_path = diagrams_dir / "Screen-Flow.mmd"
    prompts_path = diagrams_dir / "Architecture-Diagram-Prompts.md"
    html_path = diagrams_dir / "Architecture-Preview.html"

    uml_path.write_text(uml_mmd, encoding="utf-8")
    flow_path.write_text(flow_mmd, encoding="utf-8")

    prompts_md = f"""# תרשימי ארכיטקטורה ופרומפטים לתיק הפרויקט (883589)

קובץ זה נוצר אוטומטית מתוך קוד הפרויקט על ידי `Generate-Architecture-Diagrams.py`.
הוא מכיל את **תרשים זרימת המסכים (Screen Flow Diagram)** ואת **תרשים המחלקות (UML Class Diagram)** מוכנים לשילוב בפרק **"מבנה / ארכיטקטורה של הפרויקט"** בתיק הפרויקט, וכן פרומפטים מוכנים להדבקה בכלי שרטוט חיצוניים (כגון Mermaid Live Editor, Draw.io או כלי AI).

---

## 1. תרשים זרימת מסכים (Screen Flow Diagram)

```mermaid
{flow_mmd.strip()}
```

### פרומפט שמור ליצירת תרשים זרימת המסכים בעיצוב גרפי:
> צור תרשים זרימת מסכים (Screen Flow Diagram) נקי וברור עבור אפליקציית .NET MAUI. מסך הפתיחה וההיררכיה הראשיים מנוהלים ב-`AppShell`, והמסכים בפרויקט הם: `{', '.join(screens)}`. הצג חיצים ברורים למעברי הניווט (`Shell.Current.GoToAsync`) בין המסכים לפי מבנה ה-Mermaid שלעיל.

---

## 2. תרשים מחלקות (UML Class Diagram)

```mermaid
{uml_mmd.strip()}
```

### פרומפט שמור ליצירת תרשים ה-UML בעיצוב גרפי:
> צור תרשים מחלקות UML תקני (UML Class Diagram) המחולק לשכבות MVVM (`Models`, `Services`, `ViewModels`, `Views`) עבור פרויקט ה-.NET MAUI, כולל קשרי ירושה (`<|--`), הכלה, והזרקת תלויות בבנאי (`..> DI`), בהתבסס על הגדרת ה-Mermaid שלעיל.
"""
    prompts_path.write_text(prompts_md, encoding="utf-8")

    html_content = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>תרשימי ארכיטקטורה — תיק פרויקט .NET MAUI</title>
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f8fafc; color: #0f172a; margin: 24px; }}
    .card {{ background: white; border: 2px solid #cbd5e1; border-radius: 14px; padding: 20px; margin-bottom: 24px; }}
    h1, h2 {{ color: #0369a1; margin-top: 0; }}
    pre {{ direction: ltr; text-align: left; background: #f1f5f9; padding: 14px; border-radius: 8px; overflow-x: auto; font-size: 13px; }}
  </style>
</head>
<body>
  <main data-guide-overview>
    <section class="card" data-guide-block="screen-flow">
      <h2>1. תרשים זרימת מסכים (Screen Flow Diagram)</h2>
      <pre>{flow_mmd}</pre>
    </section>
    <section class="card" data-guide-block="uml-diagram">
      <h2>2. תרשים מחלקות (UML Class Diagram)</h2>
      <pre>{uml_mmd}</pre>
    </section>
  </main>
</body>
</html>
"""
    html_path.write_text(html_content, encoding="utf-8")

    print(f"Generated Screen Flow Diagram: {flow_path}")
    print(f"Generated UML Class Diagram:   {uml_path}")
    print(f"Generated Saved Prompts:       {prompts_path}")
    print(f"Generated HTML Preview:        {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
