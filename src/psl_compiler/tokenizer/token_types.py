"""
Defines the Token type: the output of the tokenizer and the input to the parser.

This is intentionally simple and stable, since both the tokenizer (Week 2) and
the parser/AST builder (Week 3) depend on this shape.
"""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """
    Software token categories for the v1 (restarted) glossary: 33 terms
    confirmed to have a real or plausible existing PSL dictionary sign,
    per data/terms.json. Extend this as more terms get confirmed.
    """

    # Functions / structure
    FUNCTION_DEF = auto()
    RETURN = auto()
    CONTINUE = auto()

    # Data / literals
    NUMBER = auto()  # abstract "number" concept/type, not a specific value
    NUMBER_LITERAL = auto()  # a specific value, e.g. from the sign for "one"
    FLOAT = auto()
    SET = auto()
    INDEX = auto()
    TYPE_CAST = auto()

    # Operators
    OP_ADD = auto()
    OP_SUBTRACT = auto()
    OP_MULTIPLY = auto()
    OP_DIVIDE = auto()
    OP_LESS_THAN = auto()
    OP_GREATER_THAN = auto()
    OP_EQUAL = auto()

    # Syntax / punctuation
    BRACE = auto()
    BRACKET = auto()
    COMMA = auto()
    PERIOD = auto()

    # OOP
    OBJECT = auto()
    CONSTRUCTOR = auto()

    # I/O
    PRINT = auto()
    FILE = auto()
    FILE_READ = auto()
    FILE_WRITE = auto()

    # Software engineering concepts
    DATABASE = auto()
    SERVER = auto()
    CLIENT = auto()
    IMPORT = auto()
    DEFAULT_PARAM = auto()
    COMPILER = auto()

    # Fallback
    UNKNOWN = auto()


@dataclass(frozen=True)
class Token:
    """
    A single software token produced by the tokenizer.

    Attributes:
        type: The category of token (see TokenType).
        value: The raw text/value associated with the token, e.g. a variable
            name or a literal value. None for pure control tokens like LOOP.
        source_id: The identifier of the PSL sign that produced this token
            (e.g. a term_id from data/terms.json), used for traceability and
            for linking back to the glossary video.
    """

    type: TokenType
    value: str | None
    source_id: str
