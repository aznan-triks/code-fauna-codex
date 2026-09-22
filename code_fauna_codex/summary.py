"""`summary` — human-readable Markdown digest of the codex, grouped by file. Offline.

A "read this before coding" artifact: every symbol's signature and first docstring
line, one heading per file. Pure text formatting of data `scan` already computed;
nothing here re-parses source. Deliberately separate from `--json`, which already
serves the machine-readable case — this is the human one.
"""
from __future__ import annotations

SECTION_TITLES = {
    "python_classes": "class",
    "python_functions": "function",
    "python_methods": "method",
}


def _docstring_first_line(docstring: str) -> str:
    for line in (docstring or "").strip().splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _rows_by_file(codex: dict) -> dict[str, list[dict]]:
    by_file: dict[str, list[dict]] = {}
    for section, rows in (codex.get("symbols") or {}).items():
        for row in rows:
            by_file.setdefault(row["file"], []).append({**row, "section": section})
    return by_file


def module_summary(codex: dict, file: str) -> str:
    """Markdown for one file's symbols, sorted by line. Empty string if the file has
    no indexed symbols (unsupported extension, or genuinely empty)."""
    rows = sorted(_rows_by_file(codex).get(file, []), key=lambda r: int(r.get("line") or 0))
    if not rows:
        return ""
    lines = [f"## {file}", ""]
    for row in rows:
        kind = SECTION_TITLES.get(row["section"], row["section"])
        doc = _docstring_first_line(row.get("docstring", ""))
        suffix = f" — {doc}" if doc else ""
        lines.append(f"- **{row['name']}** ({kind}, line {row['line']}) "
                     f"`{row.get('signature', '')}`{suffix}")
    return "\n".join(lines) + "\n"


def codex_summary(codex: dict) -> str:
    """Markdown covering every file that has at least one symbol, sorted by path."""
    by_file = _rows_by_file(codex)
    if not by_file:
        return "# Codex summary\n\nNo symbols indexed.\n"
    parts = [f"# Codex summary — {len(by_file)} file(s)\n"]
    parts.extend(module_summary(codex, file) for file in sorted(by_file))
    return "\n".join(parts)
