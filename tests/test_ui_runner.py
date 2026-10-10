"""Tests for the GUI's core logic (no display needed)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from psl_compiler.codegen.generator import CodegenError
from psl_compiler.parser.parser import ParseError
from psl_compiler.tokenizer.engine import TokenizationEngine, UnknownIdentifierError
from psl_compiler.ui.runner import run_sequence


def test_run_sequence_print_addition():
    engine = TokenizationEngine()
    code, output = run_sequence(engine, ["print_statement", "number_one", "addition", "number_two"])
    assert code == "print((1 + 2))"
    assert output.strip() == "3"


def test_run_sequence_repeat_loop_via_clicks():
    engine = TokenizationEngine()
    clicks = ["repeat_statement", "number_three", "curly_bracket",
              "print_statement", "number_one", "curly_bracket"]
    _, output = run_sequence(engine, clicks)
    assert output.strip().splitlines() == ["1", "1", "1"]


def test_run_sequence_unknown_sign_raises():
    with pytest.raises(UnknownIdentifierError):
        run_sequence(TokenizationEngine(), ["not_a_sign"])


def test_run_sequence_bad_order_raises_parse_error():
    with pytest.raises(ParseError):
        run_sequence(TokenizationEngine(), ["addition", "addition"])


def test_run_sequence_return_raises_codegen_error():
    with pytest.raises(CodegenError):
        run_sequence(TokenizationEngine(), ["return_statement", "number_one"])
