"""
Parser: converts a list of Tokens (from the tokenizer) into an AST.

v1 scope: numeric arithmetic and comparisons (with bracket grouping),
print statements, and return statements.

v2 addition: variable assignment, if/else, and repeat loops, using
provisional PSL signs (see data/terms.json entries with
"dictionary_match": null) pending real sign development with Deaf
Reach/FESF. This also resolves an earlier ambiguity: curly brackets now
exclusively mean "block start/end" (used for if/else and repeat bodies)
rather than doubling as expression grouping -- square brackets are the
only grouping delimiter now.

Still not supported: lists/arrays, real function bodies, arbitrary
variable names (only three provisional slots: variable_a/b/c).

Grammar (informal):
    program      := statement*
    block        := BRACE statement* BRACE
    statement    := print_stmt | return_stmt | assignment | if_stmt
                     | repeat_stmt | expression
    print_stmt   := PRINT expression
    return_stmt  := RETURN expression
    assignment   := VARIABLE ASSIGN expression
    if_stmt      := IF expression block (ELSE block)?
    repeat_stmt  := REPEAT expression block
    expression   := comparison
    comparison   := additive ((OP_LESS_THAN | OP_GREATER_THAN | OP_EQUAL) additive)*
    additive     := term ((OP_ADD | OP_SUBTRACT) term)*
    term         := primary ((OP_MULTIPLY | OP_DIVIDE) primary)*
    primary      := NUMBER | FLOAT | TRUE | FALSE | VARIABLE
                     | BRACKET expression BRACKET
"""

from psl_compiler.ast.nodes import (
    ASTNode,
    Assignment,
    BinaryExpression,
    Identifier,
    IfStatement,
    Literal,
    PrintStatement,
    Program,
    RepeatStatement,
    ReturnStatement,
)
from psl_compiler.tokenizer.token_types import Token, TokenType

_COMPARISON_OPS = {TokenType.OP_LESS_THAN, TokenType.OP_GREATER_THAN, TokenType.OP_EQUAL}
_ADDITIVE_OPS = {TokenType.OP_ADD, TokenType.OP_SUBTRACT}
_MULTIPLICATIVE_OPS = {TokenType.OP_MULTIPLY, TokenType.OP_DIVIDE}


class ParseError(Exception):
    """Raised when the token stream doesn't match the v1/v2 grammar."""


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    # -- helpers ---------------------------------------------------------

    def _peek(self, offset: int = 0) -> Token | None:
        index = self.position + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return None

    def _advance(self) -> Token:
        token = self._peek()
        if token is None:
            raise ParseError("Unexpected end of token stream.")
        self.position += 1
        return token

    def _expect(self, token_type: TokenType) -> Token:
        token = self._peek()
        if token is None or token.type != token_type:
            found = token.type.name if token is not None else "end of input"
            raise ParseError(f"Expected {token_type.name}, found {found}.")
        return self._advance()

    def _at_end(self) -> bool:
        return self.position >= len(self.tokens)

    # -- entry point -------------------------------------------------------

    def parse(self) -> Program:
        """Build and return the root Program AST node from self.tokens."""
        body: list[ASTNode] = []
        while not self._at_end():
            body.append(self._parse_statement())
        return Program(body=body)

    # -- blocks --------------------------------------------------------------

    def _parse_block(self) -> list[ASTNode]:
        """A BRACE-delimited sequence of statements: { stmt* }."""
        self._expect(TokenType.BRACE)
        statements: list[ASTNode] = []
        while (tok := self._peek()) is not None and tok.type != TokenType.BRACE:
            statements.append(self._parse_statement())
        self._expect(TokenType.BRACE)
        return statements

    # -- statements --------------------------------------------------------

    def _parse_statement(self) -> ASTNode:
        token = self._peek()
        if token is None:
            raise ParseError("Expected a statement but reached end of input.")

        if token.type == TokenType.PRINT:
            self._advance()
            return PrintStatement(value=self._parse_expression())

        if token.type == TokenType.RETURN:
            self._advance()
            return ReturnStatement(value=self._parse_expression())

        if token.type == TokenType.IF:
            self._advance()
            condition = self._parse_expression()
            then_body = self._parse_block()
            else_body = None
            if (tok := self._peek()) is not None and tok.type == TokenType.ELSE:
                self._advance()
                else_body = self._parse_block()
            return IfStatement(condition=condition, then_body=then_body, else_body=else_body)

        if token.type == TokenType.REPEAT:
            self._advance()
            count = self._parse_expression()
            body = self._parse_block()
            return RepeatStatement(count=count, body=body)

        if token.type == TokenType.VARIABLE:
            next_tok = self._peek(1)
            if next_tok is not None and next_tok.type == TokenType.ASSIGN:
                name = self._advance().value  # the VARIABLE token
                self._advance()  # the ASSIGN token
                value = self._parse_expression()
                return Assignment(target=name, value=value)

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

        if token.type == TokenType.TRUE:
            self._advance()
            return Literal(value=True)

        if token.type == TokenType.FALSE:
            self._advance()
            return Literal(value=False)

        if token.type == TokenType.VARIABLE:
            self._advance()
            return Identifier(name=token.value)

        if token.type == TokenType.BRACKET:
            self._advance()
            inner = self._parse_expression()
            self._expect(TokenType.BRACKET)
            return inner

        raise ParseError(f"Unexpected token in expression: {token.type.name}")
