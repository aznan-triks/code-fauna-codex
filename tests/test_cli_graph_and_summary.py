"""Tests — code_fauna_codex.cli `graph` and `summary` subcommands."""
from __future__ import annotations

import json

from conftest import write

from code_fauna_codex.cli import main


def _scanned_codex(tmp_path):
    write(tmp_path, "mod.py", "def top():\n    helper()\n\n\ndef helper():\n    pass\n")
    codex_path = tmp_path / "codex.json"
    main(["scan", str(tmp_path), "--out", str(codex_path)])
    return codex_path


def test_graph_prints_mermaid_by_default(tmp_path, capsys):
    codex_path = _scanned_codex(tmp_path)
    capsys.readouterr()
    code = main(["graph", "--codex", str(codex_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith("flowchart LR")
    assert "top" in out and "helper" in out


def test_graph_dot_format_writes_to_out(tmp_path):
    codex_path = _scanned_codex(tmp_path)
    out_path = tmp_path / "graph.dot"
    code = main(["graph", "--codex", str(codex_path), "--format", "dot", "--out", str(out_path)])
    assert code == 0
    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("digraph codex {")


def test_graph_json_mode_returns_content_key(tmp_path, capsys):
    codex_path = _scanned_codex(tmp_path)
    capsys.readouterr()
    code = main(["graph", "--codex", str(codex_path), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["ok"] is True
    assert payload["command"] == "graph"
    assert "flowchart LR" in payload["content"]


def test_graph_missing_codex_exits_needs_user(tmp_path, capsys):
    code = main(["graph", "--codex", str(tmp_path / "missing.json")])
    assert code == 2


def test_summary_whole_codex_lists_every_file(tmp_path, capsys):
    codex_path = _scanned_codex(tmp_path)
    capsys.readouterr()
    code = main(["summary", "--codex", str(codex_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "mod.py" in out
    assert "top" in out and "helper" in out


def test_summary_single_file_filter(tmp_path, capsys):
    write(tmp_path, "other.py", "def lonely():\n    pass\n")
    codex_path = _scanned_codex(tmp_path)
    capsys.readouterr()
    code = main(["summary", "--codex", str(codex_path), "--file", "mod.py"])
    out = capsys.readouterr().out
    assert code == 0
    assert "mod.py" in out
    assert "other.py" not in out


def test_summary_unknown_file_reports_no_symbols_and_exits_zero(tmp_path, capsys):
    codex_path = _scanned_codex(tmp_path)
    capsys.readouterr()
    code = main(["summary", "--codex", str(codex_path), "--file", "nope.py"])
    out = capsys.readouterr().out
    assert code == 0
    assert "No symbols found" in out
