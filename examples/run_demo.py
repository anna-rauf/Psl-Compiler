"""
A runnable demo of the full PSL Compiler pipeline.

Usage:
    python examples/run_demo.py

Edit the `PSL_IDENTIFIERS` list below to try your own sequences -- use
the "id" values from data/terms.json (e.g. "number_one", "addition").
Run `python examples/list_terms.py` to see every valid id you can use.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from psl_compiler.codegen.generator import generate
from psl_compiler.parser.parser import Parser
from psl_compiler.tokenizer.engine import TokenizationEngine

# Try changing this to any sequence of valid term ids from data/terms.json.
# This example represents: print(1 + 2)
PSL_IDENTIFIERS = ["print_statement", "number_one", "addition", "number_two"]


def main():
    engine = TokenizationEngine()

    print("PSL identifiers (input):")
    print(" ", PSL_IDENTIFIERS)
    print()

    unknown = engine.unknown_identifiers(PSL_IDENTIFIERS)
    if unknown:
        print(f"WARNING: these identifiers aren't in the v1 glossary yet: {unknown}")
        print("Run examples/list_terms.py to see all valid ids.")
        return

    tokens = engine.tokenize_sequence(PSL_IDENTIFIERS)
    print("Tokens:")
    for t in tokens:
        print(f"  {t.source_id:20s} -> {t.type.name}" + (f" (value={t.value})" if t.value else ""))
    print()

    program = Parser(tokens).parse()
    print("AST:")
    print(" ", program)
    print()

    code = generate(program)
    print("Generated Python:")
    print(" ", code)
    print()

    print("Running the generated Python:")
    exec(code)  # noqa: S102 -- this is the whole point of the demo


if __name__ == "__main__":
    main()
