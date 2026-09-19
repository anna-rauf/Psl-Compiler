"""
Prints every term id in the v1 glossary that you can use in
examples/run_demo.py's PSL_IDENTIFIERS list, grouped by category, with a
flag for terms that still need fluent-signer verification.

Usage:
    python examples/list_terms.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from psl_compiler.glossary.loader import Glossary


def main():
    glossary = Glossary()
    by_category: dict[str, list[dict]] = {}
    for term in glossary.terms:
        by_category.setdefault(term["category"], []).append(term)

    for category in sorted(by_category):
        print(f"\n{category}")
        print("-" * len(category))
        for term in by_category[category]:
            flag = ""
            match = term.get("dictionary_match")
            if match == "partial":
                flag = "  [NEEDS VERIFICATION]"
            elif not match:
                flag = "  [no dictionary sign yet]"
            print(f"  {term['id']:22s} {term['token_type']:16s}{flag}")


if __name__ == "__main__":
    main()
