"""
Tokenization engine: maps a recognized PSL identifier to a software Token.

Week 1 scope: define the interface and a lookup-table-based implementation
that reads term -> token mappings from data/terms.json.

Week 2 scope: proper error handling for identifiers that don't match any
known term (e.g. a misrecognized sign, or a sign for a concept not yet in
the v1 glossary) via UnknownIdentifierError, plus a "safe" tokenization
mode that degrades gracefully instead of crashing -- useful once real sign
recognition is plugged in, since misrecognition will happen in practice.

Not yet implemented: the actual visual recognition step (image/video ->
PSL identifier label). This engine assumes the input is already a
pre-labeled identifier string; see the open design question in README.md.
"""

import json
from pathlib import Path

from psl_compiler.tokenizer.token_types import Token, TokenType

DEFAULT_TERMS_PATH = Path(__file__).resolve().parents[3] / "data" / "terms.json"


class UnknownIdentifierError(KeyError):
    """
    Raised when a PSL identifier doesn't match any term in the master
    glossary (data/terms.json).

    This can happen for two different reasons, which callers may want to
    handle differently:
      - the sign was misrecognized (a real term's sign, read wrong), or
      - the sign is for a real concept that isn't in the v1 glossary yet
        (e.g. "loop", which has no confirmed PSL dictionary sign -- see
        README.md for what's in/out of v1 scope).

    This engine can't tell which case it is; it just reports that the
    identifier isn't recognized.
    """

    def __init__(self, psl_identifier: str):
        self.psl_identifier = psl_identifier
        super().__init__(
            f"Unrecognized PSL identifier: '{psl_identifier}'. "
            "Not found in the v1 glossary (data/terms.json) -- either a "
            "misrecognition, or a concept not yet in scope."
        )


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

    def is_known(self, psl_identifier: str) -> bool:
        """Check whether an identifier matches a term in the glossary."""
        return psl_identifier in self._term_by_id

    def tokenize_identifier(self, psl_identifier: str, safe: bool = False) -> Token:
        """
        Convert a single recognized PSL identifier (a term id, e.g.
        "number") into a Token.

        Args:
            psl_identifier: The id of the recognized PSL sign, matching an
                "id" field in data/terms.json.
            safe: If True, an unrecognized identifier produces an UNKNOWN
                token instead of raising, so a single misrecognized sign
                doesn't halt an entire sequence. Defaults to False so
                mistakes surface loudly during development.

        Raises:
            UnknownIdentifierError: if the identifier isn't in the master
                term list and safe=False.
        """
        term = self._term_by_id.get(psl_identifier)
        if term is None:
            if safe:
                return Token(type=TokenType.UNKNOWN, value=None, source_id=psl_identifier)
            raise UnknownIdentifierError(psl_identifier)

        token_type_name = term.get("token_type", "UNKNOWN")
        token_type = TokenType[token_type_name]
        return Token(type=token_type, value=term.get("default_value"), source_id=psl_identifier)

    def tokenize_sequence(self, psl_identifiers: list[str], safe: bool = False) -> list[Token]:
        """
        Convert an ordered list of PSL identifiers into a list of Tokens.

        Args:
            psl_identifiers: Ordered PSL identifiers to tokenize.
            safe: Passed through to tokenize_identifier for each item --
                see its docstring. In safe mode, one bad identifier
                produces an UNKNOWN token rather than aborting the whole
                sequence.
        """
        return [self.tokenize_identifier(pid, safe=safe) for pid in psl_identifiers]

    def unknown_identifiers(self, psl_identifiers: list[str]) -> list[str]:
        """
        Return the subset of the given identifiers that aren't recognized,
        preserving order and without raising. Useful for pre-flight
        checking a sequence (e.g. to report all problems at once) before
        deciding whether to tokenize it in safe or strict mode.
        """
        return [pid for pid in psl_identifiers if not self.is_known(pid)]
