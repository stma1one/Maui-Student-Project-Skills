# Package Manifest

Package: MAUI Step Guide Author Skill (Source-Grounded Learning Books & Bagrut Portfolio)
Version: 1.4.1
Status: classroom-ready
Parent Package: MAUI K12 Baton Workflow Skill (v1.4.1)

## Purpose

Authoring step-by-step .NET MAUI learning books and Ministry of Education 5-unit Project Portfolios (תיק פרויקט — 883589) for new and existing projects. Guides are source-grounded, use small visual and MVVM blocks, auto-generate UML & Screen Flow architecture diagrams and saved prompts from code, use live MAUI DevFlow screenshots (`Learning/Images/`) when installed and working on the active target platform (with HTML visual models as fallback when DevFlow or an emulator is unavailable), and validate the final HTML/PDF book before publication.

## Included Files

```text
Install-Skill.ps1
Install-Skill.sh
PACKAGE-MANIFEST.md
README.md
scripts/Install-Skill.ps1
scripts/Install-Skill.sh
skills/maui-step-guide-author/SKILL.md
skills/maui-step-guide-author/evals/evals.json
skills/maui-step-guide-author/references/bagrut-portfolio-structure.md
skills/maui-step-guide-author/references/guide-template.md
skills/maui-step-guide-author/references/html-mockup-guide.md
skills/maui-step-guide-author/scripts/capture_mockup_blocks.py
skills/maui-step-guide-author/scripts/ensure_maui_devflow.py
skills/maui-step-guide-author/scripts/generate_architecture_diagrams.py
skills/maui-step-guide-author/scripts/generate_book_pdf.py
skills/maui-step-guide-author/scripts/requirements-learning-book.txt
skills/maui-step-guide-author/scripts/validate_bagrut_compliance.py
skills/maui-step-guide-author/scripts/validate_learning_book.py
```

## Skill Metadata

Name:

```text
maui-step-guide-author
```

Primary trigger:

```text
Create or extend source-grounded .NET MAUI learning books, screen guides, live MAUI DevFlow screenshots when installed and working (with HTML visual mockups as fallback), architecture diagrams (UML + Screen Flow), and validated HTML/PDF Project Portfolios (883589).
```

Compatible Hosts:

- Antigravity / Gemini CLI (.agents/skills)
- Claude Code
- Codex
