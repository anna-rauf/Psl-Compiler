"""
Launch the click-based Sign Card Builder GUI.

Usage:
    python examples/sign_card_builder.py

Click signs in order to build a program, then press Run. No typing needed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from psl_compiler.ui.app import main

if __name__ == "__main__":
    main()
