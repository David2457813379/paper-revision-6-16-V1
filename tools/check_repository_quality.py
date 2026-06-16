"""Optional static quality checks for the EUI-OCEI research package."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import nbformat


NOTEBOOK_DIR = Path("experiment_code/notebooks")
OUTPUT_DIRS = [
    Path("outputs_step1"),
    Path("outputs_step2"),
    Path("outputs_step3"),
    Path("outputs_step4"),
    Path("paper_assets"),
]
TEXT_OUTPUT_SUFFIXES = {".csv", ".txt", ".svg", ".json", ".md"}

HAN_RE = re.compile(r"[\u4e00-\u9fff]")
NON_PORTABLE_RE = re.compile(r"[\uff00-\uffef\u2013\u2014\u00b7\u00b2\u00b3]")
TOOLS_DEP_RE = re.compile(
    r"(^|\n)\s*(from\s+tools\b|import\s+tools\b)|(^|\n)\s*from\s+experiment_code\.tools\b|tools\.",
    re.MULTILINE,
)


def check_notebook_code() -> list[str]:
    failures: list[str] = []
    for notebook_path in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
        nb = nbformat.read(notebook_path, as_version=4)
        for index, cell in enumerate(nb.cells):
            if cell.cell_type != "code":
                continue
            source = cell.source or ""
            location = f"{notebook_path}:code_cell_{index}"
            if HAN_RE.search(source):
                failures.append(f"{location}: Chinese characters remain in code-cell text.")
            if NON_PORTABLE_RE.search(source):
                failures.append(f"{location}: non-portable fullwidth/superscript/dash characters remain.")
            if TOOLS_DEP_RE.search(source):
                failures.append(f"{location}: notebook depends on optional tools.")
            try:
                ast.parse(source)
            except SyntaxError as exc:
                failures.append(f"{location}: syntax error: {exc}")
    return failures


def check_generated_text_outputs() -> list[str]:
    failures: list[str] = []
    for root in OUTPUT_DIRS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.suffix.lower() not in TEXT_OUTPUT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError as exc:
                failures.append(f"{path}: cannot read text output: {exc}")
                continue
            if HAN_RE.search(text):
                failures.append(f"{path}: Chinese characters found in generated text/vector output.")
    return failures


def main() -> int:
    failures = check_notebook_code()
    failures.extend(check_generated_text_outputs())

    if failures:
        print("Repository quality check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Repository quality check passed.")
    print("- Notebook code cells are syntax-valid.")
    print("- Notebook code cells contain no Chinese text or non-portable fullwidth figure labels.")
    print("- The four notebooks do not import optional tools.")
    print("- Generated text/vector outputs contain no Chinese characters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
