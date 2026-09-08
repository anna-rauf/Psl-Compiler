"""
Abstract Syntax Tree node definitions.

v1 scope: only nodes for concepts with a confirmed or candidate PSL
dictionary sign (see data/terms.json / README.md). Notably absent:
VariableAssignment, LoopBlock, ConditionalBlock -- variables, loops, and
if/else have no PSL dictionary match yet, so a parser can't honestly build
these until that vocabulary exists (see README's "Not yet supported in
v1"). Add them back once those signs are confirmed or coined.
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
    """A numeric literal (from a NUMBER or FLOAT token)."""

    value: int | float


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
class PrintStatement(ASTNode):
    """A print statement wrapping a single expression."""

    value: ASTNode


@dataclass
class ReturnStatement(ASTNode):
    """A return statement wrapping a single expression."""

    value: ASTNode
