"""
Demo: repeat loop using real PSL identifiers.

Represents: repeat 3 times: print 1

Usage:
    python examples/demo_loop.py
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
    tokens = [
        engine.tokenize_identifier("repeat_statement"),
        engine.tokenize_identifier("number_three"),
        Token(type=TokenType.BRACE, value=None, source_id="curly_bracket"),
        engine.tokenize_identifier("print_statement"),
        engine.tokenize_identifier("number_one"),
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
