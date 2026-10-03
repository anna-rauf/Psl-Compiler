"""
Abstract Syntax Tree node definitions.

v1 scope: nodes for concepts with a confirmed or candidate PSL dictionary
sign (see data/terms.json / README.md), plus a v2 addition below for
variables, if/else, and repeat -- using provisional signs agreed as
placeholders pending real sign development with Deaf Reach/FESF (see
data/terms.json entries with "dictionary_match": null and their notes).
Still absent: lists/arrays, real function bodies, and user-defined
function/parameter names -- no PSL sign concept exists yet for any of
these.
"""

from dataclasses import dataclass, field


@dataclass
class ASTNode:
    """Base class for all AST nodes."""


@dataclass
class Program(ASTNode):
    """The root node: an ordered list of top-level statements."""

    body: list[ASTNode] = field(default_factory=list)


@dataclass
class Literal(ASTNode):
    """A numeric or boolean literal (from a NUMBER, FLOAT, TRUE, or FALSE token)."""

    value: int | float | bool


@dataclass
class Identifier(ASTNode):
    """
    A reference to a variable, e.g. the "x" in "print x" or "x + 1".

    name is a plain Python-safe variable name (e.g. "a"), taken from a
    VARIABLE token's value. v1 only has three provisional variable slots
    (variable_a/b/c in data/terms.json) since there's no PSL sign concept
    yet for arbitrary user-defined names -- see README's open design
    question on function naming, which applies here too.
    """

    name: str


@dataclass
class BinaryExpression(ASTNode):
    """
    A binary operation, e.g. Literal(2) OP_ADD Literal(3).

    operator is the TokenType name (e.g. "OP_ADD", "OP_LESS_THAN") rather
    than a raw symbol, so it stays traceable back to the PSL sign that
    produced it.
    """

    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class Assignment(ASTNode):
    """A variable assignment, e.g. "x = 1 + 2"."""

    target: str
    value: ASTNode


@dataclass
class IfStatement(ASTNode):
    """
    An if (optionally if/else) statement.

    condition is any expression (comparisons like OP_LESS_THAN are the
    expected case, since there's no dedicated boolean-expression grammar
    yet). else_body is None when there's no else clause.
    """

    condition: ASTNode
    then_body: list[ASTNode]
    else_body: list[ASTNode] | None = None


@dataclass
class RepeatStatement(ASTNode):
    """
    A "repeat N times" loop -- the provisional v1 stand-in for a general
    loop construct, since there's no PSL sign yet for while/for
    specifically. count is an expression (usually a Literal) giving how
    many times to run body.
    """

    count: ASTNode
    body: list[ASTNode]


@dataclass
class PrintStatement(ASTNode):
    """A print statement wrapping a single expression."""

    value: ASTNode


@dataclass
class ReturnStatement(ASTNode):
    """A return statement wrapping a single expression."""

    value: ASTNode
