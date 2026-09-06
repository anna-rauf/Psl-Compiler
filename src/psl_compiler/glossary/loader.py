"""
Loads and queries the master term list (data/terms.json).

This is the single source of truth for:
  - which computing terms exist (the 150+ term list)
  - which token type each term maps to (used by the tokenizer)
  - which terms already have a recorded glossary video, and which don't
"""

import json
from pathlib import Path

DEFAULT_TERMS_PATH = Path(__file__).resolve().parents[3] / "data" / "terms.json"


class Glossary:
    def __init__(self, terms_path: Path = DEFAULT_TERMS_PATH):
        self.terms_path = terms_path
        with open(terms_path, encoding="utf-8") as f:
            self._data = json.load(f)
        self.terms: list[dict] = self._data["terms"]

    def __len__(self) -> int:
        return len(self.terms)

    def by_category(self) -> dict[str, list[dict]]:
        """Group terms by category."""
        grouped: dict[str, list[dict]] = {}
        for term in self.terms:
            grouped.setdefault(term["category"], []).append(term)
        return grouped

    def get(self, term_id: str) -> dict:
        for term in self.terms:
            if term["id"] == term_id:
                return term
        raise KeyError(f"No term with id '{term_id}'")

    def recorded_videos(self) -> list[dict]:
        return [t for t in self.terms if t["video_status"] == "recorded"]

    def pending_videos(self) -> list[dict]:
        return [t for t in self.terms if t["video_status"] != "recorded"]

    def mark_recorded(self, term_id: str, psl_video_id: str) -> None:
        """Update a term's status once its glossary video has been filmed."""
        term = self.get(term_id)
        term["video_status"] = "recorded"
        term["psl_video_id"] = psl_video_id
        with open(self.terms_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    g = Glossary()
    print(f"Total terms: {len(g)}")
    for category, terms in g.by_category().items():
        print(f"  {category}: {len(terms)} terms")
