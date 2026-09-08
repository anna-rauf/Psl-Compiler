"""
Week 1 sanity tests: confirm the term list is well-formed and the tokenizer
can load it and produce tokens for entries that have a real token_type.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from psl_compiler.ast.nodes import BinaryExpression, Literal, PrintStatement, ReturnStatement
from psl_compiler.glossary.loader import Glossary
from psl_compiler.parser.parser import ParseError, Parser
from psl_compiler.tokenizer.engine import TokenizationEngine, UnknownIdentifierError
from psl_compiler.tokenizer.token_types import Token, TokenType


def test_term_list_has_at_least_30_terms():
    glossary = Glossary()
    assert len(glossary) >= 30


def test_every_term_has_required_fields():
    glossary = Glossary()
    required = {"id", "term", "category", "token_type", "video_status"}
    for term in glossary.terms:
        assert required.issubset(term.keys())


def test_term_ids_are_unique():
    glossary = Glossary()
    ids = [t["id"] for t in glossary.terms]
    assert len(ids) == len(set(ids))


def test_tokenizer_can_tokenize_a_known_term():
    engine = TokenizationEngine()
    token = engine.tokenize_identifier("number")
    assert token.type == TokenType.NUMBER
    assert token.source_id == "number"


def test_tokenizer_raises_on_unknown_identifier():
    engine = TokenizationEngine()
    try:
        engine.tokenize_identifier("not_a_real_term")
        assert False, "expected UnknownIdentifierError"
    except UnknownIdentifierError as e:
        assert e.psl_identifier == "not_a_real_term"


def test_tokenizer_safe_mode_does_not_raise():
    engine = TokenizationEngine()
    token = engine.tokenize_identifier("not_a_real_term", safe=True)
    assert token.type == TokenType.UNKNOWN
    assert token.source_id == "not_a_real_term"


def test_tokenizer_safe_sequence_mixes_known_and_unknown():
    engine = TokenizationEngine()
    tokens = engine.tokenize_sequence(["number", "not_a_real_term", "addition"], safe=True)
    assert [t.type for t in tokens] == [TokenType.NUMBER, TokenType.UNKNOWN, TokenType.OP_ADD]


def test_unknown_identifiers_reports_only_bad_ones():
    engine = TokenizationEngine()
    bad = engine.unknown_identifiers(["number", "loop", "addition", "if_statement"])
    assert bad == ["loop", "if_statement"]


def test_is_known():
    engine = TokenizationEngine()
    assert engine.is_known("number") is True
    assert engine.is_known("loop") is False


def _num(value):
    return Token(type=TokenType.NUMBER, value=value, source_id="number")


def _op(token_type):
    return Token(type=token_type, value=None, source_id="op")


def test_parser_simple_addition():
    tokens = [_num(2), _op(TokenType.OP_ADD), _num(3)]
    program = Parser(tokens).parse()
    expr = program.body[0]
    assert isinstance(expr, BinaryExpression)
    assert expr.operator == "OP_ADD"
    assert expr.left == Literal(value=2)
    assert expr.right == Literal(value=3)


def test_parser_respects_operator_precedence():
    # 2 + 3 * 4 should parse as 2 + (3 * 4), not (2 + 3) * 4
    tokens = [_num(2), _op(TokenType.OP_ADD), _num(3), _op(TokenType.OP_MULTIPLY), _num(4)]
    expr = Parser(tokens).parse().body[0]
    assert expr.operator == "OP_ADD"
    assert expr.left == Literal(value=2)
    assert isinstance(expr.right, BinaryExpression)
    assert expr.right.operator == "OP_MULTIPLY"


def test_parser_bracket_grouping_overrides_precedence():
    # (2 + 3) * 4 should parse with the addition happening first
    tokens = [
        _op(TokenType.BRACKET),
        _num(2),
        _op(TokenType.OP_ADD),
        _num(3),
        _op(TokenType.BRACKET),
        _op(TokenType.OP_MULTIPLY),
        _num(4),
    ]
    expr = Parser(tokens).parse().body[0]
    assert expr.operator == "OP_MULTIPLY"
    assert isinstance(expr.left, BinaryExpression)
    assert expr.left.operator == "OP_ADD"


def test_parser_print_statement():
    tokens = [_op(TokenType.PRINT), _num(5)]
    stmt = Parser(tokens).parse().body[0]
    assert isinstance(stmt, PrintStatement)
    assert stmt.value == Literal(value=5)


def test_parser_return_statement():
    tokens = [_op(TokenType.RETURN), _num(1), _op(TokenType.OP_ADD), _num(1)]
    stmt = Parser(tokens).parse().body[0]
    assert isinstance(stmt, ReturnStatement)
    assert isinstance(stmt.value, BinaryExpression)


def test_parser_raises_on_mismatched_bracket():
    tokens = [_op(TokenType.BRACKET), _num(1)]
    try:
        Parser(tokens).parse()
        assert False, "expected ParseError"
    except ParseError:
        pass
