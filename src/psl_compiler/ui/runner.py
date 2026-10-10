"""
Core logic for running a built sequence of PSL identifiers, kept
separate from the Tkinter GUI (app.py) so it's testable without a
display server.
"""

import io
from contextlib import redirect_stdout

from psl_compiler.codegen.generator import generate
from psl_compiler.parser.parser import Parser
from psl_compiler.tokenizer.engine import TokenizationEngine


def run_sequence(engine: TokenizationEngine, sequence: list[str]) -> tuple[str, str]:
    """
    Tokenize, parse, generate, and execute a sequence of glossary term
    ids (e.g. ["number_one", "addition", "number_two"]).

    Returns:
        (generated_code, captured_stdout)

    Raises:
        UnknownIdentifierError: an id isn't in the glossary.
        ParseError: the sequence doesn't match the grammar.
        CodegenError: the AST contains something that can't be
            generated yet (e.g. a top-level return).
        Any exception the generated code itself raises when executed.
    """
    tokens = engine.tokenize_sequence(sequence)
    program = Parser(tokens).parse()
    code = generate(program)

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exec(code)  # noqa: S102 -- code built entirely from our own glossary/grammar

    return code, buffer.getvalue()
