"""`graph` — export the codex's call/import edges as Mermaid or DOT text. Offline.

Pure text formatting of the `edges` block `scan` already computed; nothing here
re-parses source or discovers new relations. Two edge kinds because they have
different shapes: `calls` pairs a caller qualname with a callee qualname, `imports`
pairs a file with a dotted module name.
"""
from __future__ import annotations

Pair = tuple[str, str]


def calls_edges(codex: dict) -> list[Pair]:
    rows = codex.get("edges", {}).get("calls", [])
    return sorted({(row["caller"], row["callee"]) for row in rows})


def import_edges(codex: dict) -> list[Pair]:
    imports = codex.get("edges", {}).get("imports", {})
    return sorted({(file, module) for file, modules in imports.items() for module in modules})


EDGE_KINDS = {"calls": calls_edges, "imports": import_edges}


def _mermaid_id(label: str, seen: dict[str, str]) -> str:
    """Map an arbitrary label to a stable, valid Mermaid node id — qualnames contain
    dots and files contain slashes, neither valid unquoted in a Mermaid node id."""
    if label not in seen:
        seen[label] = f"n{len(seen)}"
    return seen[label]


def to_mermaid(pairs: list[Pair]) -> str:
    lines = ["flowchart LR"]
    seen: dict[str, str] = {}
    for src, dst in pairs:
        a, b = _mermaid_id(src, seen), _mermaid_id(dst, seen)
        lines.append(f'  {a}["{src}"] --> {b}["{dst}"]')
    return "\n".join(lines) + "\n"


def to_dot(pairs: list[Pair]) -> str:
    lines = ["digraph codex {"]
    for src, dst in pairs:
        lines.append(f'  "{src}" -> "{dst}";')
    lines.append("}")
    return "\n".join(lines) + "\n"


EXPORTERS = {"mermaid": to_mermaid, "dot": to_dot}
