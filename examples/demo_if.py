"""
Demo: if/else using real PSL identifiers.

Represents: a = 5; if a > 2: print 1 else: print 0

Usage:
    python examples/demo_if.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from psl_compiler.codegen.generator import generate
from psl_compiler.parser.parser import Parser
from psl_compiler.tokenizer.engine import TokenizationEngine
from psl_compiler.tokenizer.token_types import Token, TokenType


def main():
    engine = TokenizationEngine()

    # The glossary has one "curly_bracket" sign used positionally for both
    # the opening and closing brace of a block (same sign, same as how
    # grouping brackets already worked) -- so we add those BRACE tokens by
    # hand rather than via tokenize_sequence, same as the test suite does.
    tokens = engine.tokenize_sequence(
        ["variable_a", "assign", "number_five",
         "if_statement", "variable_a", "greater_than", "number_two"]
    )
    tokens += [
        Token(type=TokenType.BRACE, value=None, source_id="curly_bracket"),
        engine.tokenize_identifier("print_statement"),
        engine.tokenize_identifier("number_one"),
        Token(type=TokenType.BRACE, value=None, source_id="curly_bracket"),
        engine.tokenize_identifier("else_statement"),
        Token(type=TokenType.BRACE, value=None, source_id="curly_bracket"),
        engine.tokenize_identifier("print_statement"),
        # Note: the glossary has no sign for "zero" yet, so the else
        # branch prints a different literal (two) to clearly show which
        # branch actually ran.
        engine.tokenize_identifier("number_two"),
        Token(type=TokenType.BRACE, value=None, source_id="curly_bracket"),
    ]

    program = Parser(tokens).parse()
    code = generate(program)
    print("Generated Python:")
    print(code)
    print()
    print("Running it:")
    exec(code)  # noqa: S102


if __name__ == "__main__":
    main()
