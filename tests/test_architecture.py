"""
Week 1 sanity tests: confirm the term list is well-formed and the tokenizer
can load it and produce tokens for entries that have a real token_type.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from psl_compiler.glossary.loader import Glossary
from psl_compiler.tokenizer.engine import TokenizationEngine
from psl_compiler.tokenizer.token_types import TokenType


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
        assert False, "expected KeyError"
    except KeyError:
        pass
