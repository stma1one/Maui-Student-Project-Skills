# MAUI Step Guide Author

This skill turns a .NET MAUI project into a source-grounded learning book.

It supports three common teaching needs:

1. **A build-along book for a new project**: start from the empty or starter project and grow the book one small milestone at a time.
2. **A roadmap and chapters for an existing project**: inspect the current repository, agree on the learning goal, and break the gap into small source-grounded steps.
3. **A UI-replication guide**: explain a screen block by block, using labelled HTML visual-model snapshots only when an emulator screenshot is unavailable.

## Quality Gate

The bundled PDF builder runs `validate_learning_book.py` by default. A book is not ready to publish if the validation report flags:

- missing or unresolved images;
- horizontally clipped or overflowing code/table blocks;
- empty PDF pages;
- text outside a PDF page boundary; or
- unreplaced template placeholders.

## Prerequisites

Install the declared Python packages and browser runtime before rendering snapshots or PDFs:

```powershell
python -m pip install -r .\Scripts\Learning-Book-Requirements.txt
python -m playwright install chromium
```
