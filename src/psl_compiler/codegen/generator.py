"""
Code generator: walks the AST and emits real, runnable Python source.

v1 scope: arithmetic/comparison expressions, print statements.

v2 addition: variable assignment, if/else, and repeat loops -- with
proper indentation support for nested blocks (4 spaces per level).

Known, now-enforced limitation: a ReturnStatement anywhere in the
program raises CodegenError rather than silently emitting invalid
Python. `return` is only legal inside a function body in real Python,
and this compiler doesn't support parsing/generating function bodies
yet (no PSL sign concept exists yet for user-defined function names --
see README's open design questions). Previously this just emitted a
bare "return ..." line that would fail with SyntaxError when run; now
the failure is explicit and explained at compile time instead.
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

_OPERATOR_SYMBOLS = {
    "OP_ADD": "+",
    "OP_SUBTRACT": "-",
    "OP_MULTIPLY": "*",
    "OP_DIVIDE": "/",
    "OP_LESS_THAN": "<",
    "OP_GREATER_THAN": ">",
    "OP_EQUAL": "==",
}

_INDENT = "    "  # four spaces per level, per the review's fix


class CodegenError(Exception):
    """Raised when an AST node can't be turned into valid Python yet."""


def generate(program: Program) -> str:
    """
    Turn a Program AST node into a Python source string.

    Raises:
        CodegenError: if the program contains a node this generator
            can't safely turn into valid Python (e.g. a ReturnStatement
            outside a function -- see module docstring).
    """
    lines = _generate_block(program.body, indent=0)
    return "\n".join(lines)


def _generate_block(statements: list[ASTNode], indent: int) -> list[str]:
    lines: list[str] = []
    for stmt in statements:
        lines.extend(_generate_statement(stmt, indent))
    return lines


def _generate_statement(node: ASTNode, indent: int) -> list[str]:
    pad = _INDENT * indent

    if isinstance(node, PrintStatement):
        return [f"{pad}print({_generate_expression(node.value)})"]

    if isinstance(node, ReturnStatement):
        raise CodegenError(
            "'return' is only valid inside a function body. This compiler "
            "doesn't support parsing function bodies yet, so a 'return' "
            "here would generate invalid Python -- raising here instead of "
            "silently emitting broken code."
        )

    if isinstance(node, Assignment):
        return [f"{pad}{node.target} = {_generate_expression(node.value)}"]

    if isinstance(node, IfStatement):
        lines = [f"{pad}if {_generate_expression(node.condition)}:"]
        lines.extend(_generate_block(node.then_body, indent + 1) or [f"{pad}{_INDENT}pass"])
        if node.else_body is not None:
            lines.append(f"{pad}else:")
            lines.extend(_generate_block(node.else_body, indent + 1) or [f"{pad}{_INDENT}pass"])
        return lines

    if isinstance(node, RepeatStatement):
        lines = [f"{pad}for _ in range({_generate_expression(node.count)}):"]
        lines.extend(_generate_block(node.body, indent + 1) or [f"{pad}{_INDENT}pass"])
        return lines

    # A bare expression used as a statement -- valid Python, if not
    # very useful on its own.
    return [f"{pad}{_generate_expression(node)}"]


def _generate_expression(node: ASTNode) -> str:
    if isinstance(node, Literal):
        return repr(node.value)
    if isinstance(node, Identifier):
        return node.name
    if isinstance(node, BinaryExpression):
        symbol = _OPERATOR_SYMBOLS.get(node.operator)
        if symbol is None:
            raise CodegenError(f"No Python operator mapping for {node.operator}")
        return f"({_generate_expression(node.left)} {symbol} {_generate_expression(node.right)})"
    raise CodegenError(f"Don't know how to generate code for {type(node).__name__}")
