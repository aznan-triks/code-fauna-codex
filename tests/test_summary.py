"""Tests — code_fauna_codex.summary (pure Markdown formatting, zero I/O, zero network)."""
from __future__ import annotations

from code_fauna_codex.summary import codex_summary, module_summary

CODEX = {
    "symbols": {
        "python_functions": [
            {"name": "hello", "file": "mod.py", "line": 3, "signature": "def hello()",
             "docstring": "Greets.\n\nMore detail.", "language": "python"},
        ],
        "python_classes": [
            {"name": "Greeter", "file": "mod.py", "line": 1, "signature": "class Greeter",
             "docstring": "", "language": "python"},
        ],
    }
}


def test_module_summary_orders_by_line_and_includes_docstring_first_line():
    out = module_summary(CODEX, "mod.py")
    assert out.index("Greeter") < out.index("hello")
    assert "Greets." in out
    assert "More detail." not in out


def test_module_summary_no_docstring_omits_dash_suffix():
    out = module_summary(CODEX, "mod.py")
    lines = out.splitlines()
    greeter_line = next(line for line in lines if "Greeter" in line)
    assert " — " not in greeter_line


def test_module_summary_unknown_file_is_empty_string():
    assert module_summary(CODEX, "nope.py") == ""


def test_codex_summary_covers_every_file_sorted():
    codex = {"symbols": {"python_functions": [
        {"name": "b1", "file": "b.py", "line": 1, "signature": "def b1()", "docstring": "", "language": "python"},
        {"name": "a1", "file": "a.py", "line": 1, "signature": "def a1()", "docstring": "", "language": "python"},
    ]}}
    out = codex_summary(codex)
    assert out.index("a.py") < out.index("b.py")


def test_codex_summary_empty_codex():
    out = codex_summary({})
    assert "No symbols indexed" in out
