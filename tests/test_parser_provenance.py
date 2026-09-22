"""Tests — Symbol.parser provenance (ast / treesitter / regex) and the schema bump
that shipped it (CODEX_SCHEMA_VERSION 1 -> 2)."""
from __future__ import annotations

import pytest
from conftest import write

from code_fauna_codex.index_store import CODEX_SCHEMA_VERSION, codex_schema_error
from code_fauna_codex.parsers.treesitter_parser import TREESITTER_AVAILABLE
from code_fauna_codex.scan import build_codex

needs_treesitter = pytest.mark.skipif(not TREESITTER_AVAILABLE, reason="tree-sitter extras not installed")


def _all_parsers(codex: dict) -> set[str]:
    return {row["parser"] for rows in codex["symbols"].values() for row in rows}


def test_python_symbols_are_tagged_ast(tmp_path):
    write(tmp_path, "mod.py", "def foo():\n    pass\n\n\nclass Bar:\n    pass\n")
    codex = build_codex(tmp_path)
    assert _all_parsers(codex) == {"ast"}


def test_regex_mode_tags_symbols_regex(tmp_path):
    write(tmp_path, "mod.js", "function foo() {}\n")
    codex = build_codex(tmp_path, parser_mode="regex")
    assert _all_parsers(codex) == {"regex"}


@needs_treesitter
def test_treesitter_mode_tags_symbols_treesitter(tmp_path):
    write(tmp_path, "mod.js", "function foo() {}\n")
    codex = build_codex(tmp_path, parser_mode="treesitter")
    assert _all_parsers(codex) == {"treesitter"}


def test_codex_schema_version_bumped_to_2():
    assert CODEX_SCHEMA_VERSION == 2


def test_pre_provenance_codex_is_rejected_not_silently_misread(tmp_path):
    """A codex written before `parser` existed (schema 1) must fail loud, not be
    half-trusted with a missing field. Locks the deliberate bump against regressing
    back to a silent read — same doctrine as the `--min-score` semantics test."""
    old_codex = {"schema_version": 1, "files": {}, "symbols": {}}
    path = tmp_path / "codex.json"
    error = codex_schema_error(old_codex, path)
    assert error is not None
    assert "scan" in error.lower()
