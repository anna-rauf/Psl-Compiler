"""
Parser: converts a list of Tokens (from the tokenizer) into an AST.

Not implemented yet — this is the Week 3 task. Left here as a stub so the
import path and interface are settled now, in Week 1.
"""

from psl_compiler.ast.nodes import Program
from psl_compiler.tokenizer.token_types import Token


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    def parse(self) -> Program:
        """Build and return the root Program AST node from self.tokens."""
        raise NotImplementedError("Parsing rules land in Week 3.")
