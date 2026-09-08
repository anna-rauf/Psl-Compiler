"""
Code generator: walks the AST and emits real, runnable Python source.

v1 scope: matches what the parser can currently produce -- arithmetic and
comparison expressions, print statements, and return statements. No
functions, loops, conditionals, or variables yet (see ast/nodes.py and
README.md for why: those concepts have no confirmed PSL sign yet).

Known limitation: a bare ReturnStatement at the top level of a program is
NOT valid standalone Python (Python only allows `return` inside a
function body). This generator emits it anyway, since deciding how to
wrap it (e.g. auto-wrapping in a function) is a Week 3+ design question
tied to how function definitions get parsed. Until then, generated code
containing a top-level return needs to be pasted inside a function by
hand before it will run.
"""

from psl_compiler.ast.nodes import (
    ASTNode,
    BinaryExpression,
    Literal,
    PrintStatement,
    Program,
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


class CodegenError(Exception):
    """Raised when an AST node can't be turned into Python yet."""


def generate(program: Program) -> str:
    """
    Turn a Program AST node into a Python source string, one statement
    per line.
    """
    lines = [_generate_statement(node) for node in program.body]
    return "\n".join(lines)


def _generate_statement(node: ASTNode) -> str:
    if isinstance(node, PrintStatement):
        return f"print({_generate_expression(node.value)})"
    if isinstance(node, ReturnStatement):
        return f"return {_generate_expression(node.value)}"
    # A bare expression used as a statement (e.g. just "1 + 2" with no
    # print/return) is valid Python, if not very useful on its own.
    return _generate_expression(node)


def _generate_expression(node: ASTNode) -> str:
    if isinstance(node, Literal):
        return repr(node.value)
    if isinstance(node, BinaryExpression):
        symbol = _OPERATOR_SYMBOLS.get(node.operator)
        if symbol is None:
            raise CodegenError(f"No Python operator mapping for {node.operator}")
        return f"({_generate_expression(node.left)} {symbol} {_generate_expression(node.right)})"
    raise CodegenError(f"Don't know how to generate code for {type(node).__name__}")
