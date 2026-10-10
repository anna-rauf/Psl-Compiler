"""
Sign Card Builder: a click-based GUI for building a program out of PSL
glossary terms, with no typing required.

This is the student-facing interface the project's core pitch depends
on -- without it, a learner has to type English identifier strings
(e.g. "number_one") to use the compiler, which defeats the point. Here,
every available sign is a button; clicking buttons in order builds a
program, and Run executes it.

Usage:
    python examples/sign_card_builder.py

Honesty note shown in the UI: provisional signs (no PSL dictionary
match yet -- variables, if/else, repeat, true/false) and partial
matches (needs fluent-signer verification) are visually flagged on
their buttons, not hidden.
"""

import tkinter as tk
import webbrowser
from tkinter import scrolledtext, ttk

from psl_compiler.glossary.loader import Glossary
from psl_compiler.tokenizer.engine import TokenizationEngine, UnknownIdentifierError
from psl_compiler.parser.parser import ParseError
from psl_compiler.codegen.generator import CodegenError
from psl_compiler.ui.runner import run_sequence


def _button_label(term: dict) -> str:
    label = term["term"]
    if term.get("dictionary_match") is None:
        label += "  (provisional)"
    elif term.get("dictionary_match") == "partial":
        label += "  (unverified)"
    return label


class SignCardApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PSL Compiler -- Sign Card Builder")
        self.engine = TokenizationEngine()
        self.glossary = Glossary()
        self.sequence: list[str] = []  # term ids, in the order clicked
        self._display_names: list[str] = []  # matching human-readable labels

        self._build_ui()

    # -- UI construction ---------------------------------------------------

    def _build_ui(self) -> None:
        root = self.root
        root.geometry("1000x650")

        main = ttk.Frame(root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        # Left: scrollable palette of sign-card buttons, grouped by category.
        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 8))

        ttk.Label(left, text="Signs", font=("", 12, "bold")).pack(anchor="w")

        canvas = tk.Canvas(left, width=360, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
        palette = ttk.Frame(canvas)
        palette.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=palette, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Mouse-wheel scrolling (Windows/macOS use <MouseWheel>; Linux uses Button-4/5).
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        for category, terms in self.glossary.by_category().items():
            ttk.Label(palette, text=category, font=("", 10, "bold")).pack(anchor="w", pady=(6, 2))
            for term in terms:
                row = ttk.Frame(palette)
                row.pack(anchor="w", pady=1)
                ttk.Button(
                    row,
                    text=_button_label(term),
                    width=30,
                    command=lambda tid=term["id"], name=term["term"]: self._add_sign(tid, name),
                ).pack(side=tk.LEFT)
                # Opens the official PSL dictionary entry (linked out, not
                # re-hosted, per (c)FESF). Disabled for provisional signs,
                # which have no dictionary entry yet.
                url = term.get("dictionary_url")
                watch = ttk.Button(
                    row,
                    text="\u25b6",
                    width=3,
                    command=lambda u=url: webbrowser.open(u),
                )
                watch.pack(side=tk.LEFT, padx=(2, 0))
                if not url:
                    watch.state(["disabled"])

        # Right: the program being built, controls, and output.
        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(
            right,
            text="Tip: click Curly Bracket once to open a block and again to close it.",
            foreground="#555555",
        ).pack(anchor="w", pady=(0, 6))
        ttk.Label(right, text="Your program (in order):", font=("", 12, "bold")).pack(anchor="w")
        self.sequence_box = tk.Listbox(right, height=10)
        self.sequence_box.pack(fill=tk.BOTH, expand=False, pady=(2, 6))

        controls = ttk.Frame(right)
        controls.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(controls, text="Undo last", command=self._undo).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(controls, text="Clear all", command=self._clear).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(controls, text="Run \u25b6", command=self._run).pack(side=tk.LEFT, padx=(0, 4))

        ttk.Label(right, text="Result:", font=("", 12, "bold")).pack(anchor="w")
        self.output_box = scrolledtext.ScrolledText(right, height=18, wrap="word")
        self.output_box.pack(fill=tk.BOTH, expand=True)
        self.output_box.configure(state="disabled")

    # -- actions -------------------------------------------------------------

    def _add_sign(self, term_id: str, display_name: str) -> None:
        self.sequence.append(term_id)
        self._display_names.append(display_name)
        self._refresh_sequence_display()

    def _undo(self) -> None:
        if self.sequence:
            self.sequence.pop()
            self._display_names.pop()
            self._refresh_sequence_display()

    def _clear(self) -> None:
        self.sequence.clear()
        self._display_names.clear()
        self._refresh_sequence_display()
        self._set_output("")

    def _refresh_sequence_display(self) -> None:
        self.sequence_box.delete(0, tk.END)
        for i, name in enumerate(self._display_names, start=1):
            self.sequence_box.insert(tk.END, f"{i}. {name}")

    def _run(self) -> None:
        if not self.sequence:
            self._set_output("Add some signs first, then press Run.")
            return
        try:
            code, output = run_sequence(self.engine, self.sequence)
            self._set_output(f"Generated Python:\n{code}\n\nOutput:\n{output}")
        except UnknownIdentifierError as e:
            self._set_output(f"Unrecognized sign: {e}")
        except ParseError as e:
            self._set_output(f"These signs aren't in a valid order yet: {e}")
        except CodegenError as e:
            self._set_output(f"Can't turn this into code yet: {e}")
        except Exception as e:  # noqa: BLE001 -- surfacing any runtime error from exec()
            self._set_output(f"Error while running: {type(e).__name__}: {e}")

    def _set_output(self, text: str) -> None:
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, text)
        self.output_box.configure(state="disabled")


def main():
    root = tk.Tk()
    SignCardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
