"""
Parser: converts a list of Tokens (from the tokenizer) into an AST.

v1 scope: recursive-descent parsing for what the 32-term glossary can
actually express -- numeric arithmetic and comparisons (with bracket
grouping), print statements, and return statements. No variables, loops,
or if/else yet: those tokens don't exist (see ast/nodes.py and
README.md's "Not yet supported in v1").

Grammar (informal):
    program      := statement*
    statement    := print_stmt | return_stmt | expression
    print_stmt   := PRINT expression
    return_stmt  := RETURN expression
    expression   := comparison
    comparison   := additive ((OP_LESS_THAN | OP_GREATER_THAN | OP_EQUAL) additive)*
    additive     := term ((OP_ADD | OP_SUBTRACT) term)*
    term         := primary ((OP_MULTIPLY | OP_DIVIDE) primary)*
    primary      := NUMBER | FLOAT | BRACE expression BRACE | BRACKET expression BRACKET
"""

from psl_compiler.ast.nodes import (
    ASTNode,
    BinaryExpression,
    Literal,
    PrintStatement,
    Program,
    ReturnStatement,
)
from psl_compiler.tokenizer.token_types import Token, TokenType

_COMPARISON_OPS = {TokenType.OP_LESS_THAN, TokenType.OP_GREATER_THAN, TokenType.OP_EQUAL}
_ADDITIVE_OPS = {TokenType.OP_ADD, TokenType.OP_SUBTRACT}
_MULTIPLICATIVE_OPS = {TokenType.OP_MULTIPLY, TokenType.OP_DIVIDE}


class ParseError(Exception):
    """Raised when the token stream doesn't match the v1 grammar."""


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    # -- helpers ---------------------------------------------------------

    def _peek(self) -> Token | None:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def _advance(self) -> Token:
        token = self._peek()
        if token is None:
            raise ParseError("Unexpected end of token stream.")
        self.position += 1
        return token

    def _at_end(self) -> bool:
        return self.position >= len(self.tokens)

    # -- entry point -------------------------------------------------------

    def parse(self) -> Program:
        """Build and return the root Program AST node from self.tokens."""
        body: list[ASTNode] = []
        while not self._at_end():
            body.append(self._parse_statement())
        return Program(body=body)

    # -- statements --------------------------------------------------------

    def _parse_statement(self) -> ASTNode:
        token = self._peek()
        if token is not None and token.type == TokenType.PRINT:
            self._advance()
            return PrintStatement(value=self._parse_expression())
        if token is not None and token.type == TokenType.RETURN:
            self._advance()
            return ReturnStatement(value=self._parse_expression())
        return self._parse_expression()

    # -- expressions (precedence climbing) ----------------------------------

    def _parse_expression(self) -> ASTNode:
        return self._parse_comparison()

    def _parse_comparison(self) -> ASTNode:
        left = self._parse_additive()
        while (tok := self._peek()) is not None and tok.type in _COMPARISON_OPS:
            operator = self._advance().type.name
            right = self._parse_additive()
            left = BinaryExpression(left=left, operator=operator, right=right)
        return left

    def _parse_additive(self) -> ASTNode:
        left = self._parse_term()
        while (tok := self._peek()) is not None and tok.type in _ADDITIVE_OPS:
            operator = self._advance().type.name
            right = self._parse_term()
            left = BinaryExpression(left=left, operator=operator, right=right)
        return left

    def _parse_term(self) -> ASTNode:
        left = self._parse_primary()
        while (tok := self._peek()) is not None and tok.type in _MULTIPLICATIVE_OPS:
            operator = self._advance().type.name
            right = self._parse_primary()
            left = BinaryExpression(left=left, operator=operator, right=right)
        return left

    def _parse_primary(self) -> ASTNode:
        token = self._peek()
        if token is None:
            raise ParseError("Expected a value but reached end of input.")

        if token.type in (TokenType.NUMBER, TokenType.FLOAT, TokenType.NUMBER_LITERAL):
            self._advance()
            if token.value is None:
                return Literal(value=0)
            try:
                value = int(token.value)
            except ValueError:
                value = float(token.value)
            return Literal(value=value)

        if token.type in (TokenType.BRACE, TokenType.BRACKET):
            opening_type = token.type
            self._advance()
            inner = self._parse_expression()
            closing = self._peek()
            if closing is None or closing.type != opening_type:
                raise ParseError(f"Expected matching {opening_type.name} to close grouping.")
            self._advance()
            return inner

        raise ParseError(f"Unexpected token in expression: {token.type.name}")
