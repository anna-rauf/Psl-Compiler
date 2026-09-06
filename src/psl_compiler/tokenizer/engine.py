"""
Tokenization engine: maps a recognized PSL identifier to a software Token.

Week 1 scope: define the interface and a lookup-table-based implementation
that reads term -> token mappings from data/terms.json.

Week 2 scope (not yet implemented): plug in the actual visual recognition
step (image/video -> PSL identifier label), if the input isn't already a
pre-labeled identifier string.
"""

import json
from pathlib import Path

from psl_compiler.tokenizer.token_types import Token, TokenType

DEFAULT_TERMS_PATH = Path(__file__).resolve().parents[3] / "data" / "terms.json"


class TokenizationEngine:
    """
    Maps PSL identifiers (term IDs) to software Tokens using the master
    term list as the source of truth.
    """

    def __init__(self, terms_path: Path = DEFAULT_TERMS_PATH):
        self.terms_path = terms_path
        self._term_by_id: dict[str, dict] = {}
        self._load_terms()

    def _load_terms(self) -> None:
        with open(self.terms_path, encoding="utf-8") as f:
            data = json.load(f)
        for term in data["terms"]:
            self._term_by_id[term["id"]] = term

    def tokenize_identifier(self, psl_identifier: str) -> Token:
        """
        Convert a single recognized PSL identifier (a term id, e.g. "loop")
        into a Token.

        Args:
            psl_identifier: The id of the recognized PSL sign, matching an
                "id" field in data/terms.json.

        Raises:
            KeyError: if the identifier isn't in the master term list.
        """
        term = self._term_by_id[psl_identifier]
        token_type_name = term.get("token_type", "UNKNOWN")
        token_type = TokenType[token_type_name]
        return Token(type=token_type, value=term.get("default_value"), source_id=psl_identifier)

    def tokenize_sequence(self, psl_identifiers: list[str]) -> list[Token]:
        """Convert an ordered list of PSL identifiers into a list of Tokens."""
        return [self.tokenize_identifier(pid) for pid in psl_identifiers]
