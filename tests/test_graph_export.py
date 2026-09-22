"""Tests — code_fauna_codex.graph_export (pure text export, zero I/O, zero network)."""
from __future__ import annotations

from code_fauna_codex.graph_export import calls_edges, import_edges, to_dot, to_mermaid


def test_calls_edges_dedupes_and_sorts():
    codex = {"edges": {"calls": [
        {"caller": "b", "callee": "z"},
        {"caller": "a", "callee": "y"},
        {"caller": "b", "callee": "z"},
    ]}}
    assert calls_edges(codex) == [("a", "y"), ("b", "z")]


def test_calls_edges_empty_codex():
    assert calls_edges({}) == []


def test_import_edges_flattens_and_sorts():
    codex = {"edges": {"imports": {"b.py": ["os"], "a.py": ["sys", "json"]}}}
    assert import_edges(codex) == [("a.py", "json"), ("a.py", "sys"), ("b.py", "os")]


def test_to_mermaid_shapes_flowchart_with_labels():
    out = to_mermaid([("Greeter.hello", "top")])
    assert out.startswith("flowchart LR\n")
    assert '["Greeter.hello"]' in out
    assert '["top"]' in out
    assert "-->" in out


def test_to_mermaid_reuses_node_id_for_repeated_label():
    out = to_mermaid([("a", "b"), ("a", "c")])
    assert out.count('n0["a"]') == 2


def test_to_mermaid_empty_pairs_still_valid_flowchart():
    assert to_mermaid([]) == "flowchart LR\n"


def test_to_dot_shapes_digraph():
    out = to_dot([("a", "b")])
    assert out == 'digraph codex {\n  "a" -> "b";\n}\n'


def test_to_dot_empty_pairs():
    assert to_dot([]) == "digraph codex {\n}\n"
