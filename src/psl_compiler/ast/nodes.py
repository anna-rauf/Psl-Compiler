"""
Abstract Syntax Tree node definitions.

Week 1 scope: sketch the node shapes so the rest of the architecture has
something concrete to import against.
Week 3 scope (not yet implemented): actual parsing rules that build these
nodes from a token stream (see src/psl_compiler/parser/).
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
class VariableAssignment(ASTNode):
    name: str
    value: ASTNode


@dataclass
class Literal(ASTNode):
    value: str | int | float


@dataclass
class LoopBlock(ASTNode):
    """Represents a loop and the statements inside it."""

    condition: ASTNode | None
    body: list[ASTNode] = field(default_factory=list)


@dataclass
class ConditionalBlock(ASTNode):
    condition: ASTNode
    body: list[ASTNode] = field(default_factory=list)
    else_body: list[ASTNode] = field(default_factory=list)


@dataclass
class FunctionDefinition(ASTNode):
    name: str
    params: list[str] = field(default_factory=list)
    body: list[ASTNode] = field(default_factory=list)
