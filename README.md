# PSL Compiler

A pipeline that converts visual PSL (sign-language) identifiers for core computing
concepts into real, runnable Python code — plus a video glossary that teaches
each term, linking to existing Pakistan Sign Language (PSL) dictionary signs
wherever one already exists.

## v2 update: variables, if/else, repeat (provisional signs)

Following an external review of this repo, four real gaps were fixed:

1. **Variables, if/else, and a repeat loop** are now parseable and
   generate real, properly-indented Python -- using *provisional*
   signs (`variable_a/b/c`, `assign`, `if_statement`, `else_statement`,
   `repeat_statement`, `true`, `false` in `data/terms.json`, each with
   `"dictionary_match": null`). These are placeholders, not confirmed
   PSL signs -- they exist so the parser/codegen/demo can be built now,
   but **must be reviewed and replaced with real signs agreed with Deaf
   Reach/FESF before use with actual learners**. Only three variable
   slots exist (`a`, `b`, `c`) since there's still no PSL sign concept
   for arbitrary user-defined names.
2. **Curly brackets now mean "block start/end"** exclusively (used by
   if/else and repeat bodies); square brackets are the only expression
   grouping delimiter. Previously both meant the same thing, which
   blocked curly brackets from ever meaning "block."
3. **The code generator now supports indentation** (4 spaces per
   nested level), required for if/else/repeat bodies to generate valid
   Python.
4. **A top-level `return` now raises a clear `CodegenError`** instead
   of silently emitting Python that would fail with `SyntaxError` when
   run. `return` is still only valid inside a function body, and
   function bodies still aren't parseable (see open design questions).

New runnable demos: `examples/demo_if.py`, `examples/demo_loop.py`.

## v1 restart scope (this Week 1)

Earlier work explored a 164-term glossary spanning full programming
fundamentals (loops, conditionals, OOP, algorithms, etc.). Checking terms
against the Deaf Reach / FESF PSL dictionary (psl.org.pk) showed that most
core control-flow vocabulary (loop, if/else, boolean) has no existing PSL
sign and would require new sign development with Deaf community
collaborators — real, valuable work, but not something to block a first
working version on.

This restart narrows the glossary to **32 terms with a real or plausible
existing PSL dictionary sign**, prioritizing confirmed coverage over
breadth. It supports: numeric literals and arithmetic, comparisons,
bracket/comma/period syntax, function definition and return, basic file
I/O, and basic object/client/server/database vocabulary.

**Not yet supported in v1** (no PSL dictionary match found): loops, if/else,
booleans, arrays. These are the next target for sign development with Deaf
Reach / FESF, not for the dictionary-matching approach used here.

Of the 32 terms, **9 are marked `partial`** in `data/terms.json` —
meaning the dictionary sign's general sense probably overlaps with the
programming sense, but this hasn't been confirmed by a fluent PSL signer.
Treat these as candidates, not final, until reviewed.

## What this project does

1. **Glossary** — `data/terms.json` / `data/terms.csv`: master list of
   computing terms, each tagged with whether a PSL dictionary sign exists
   (`dictionary_match`: `exact` / `partial` / none) and a link to it.
   `video_status` tracks where the teaching video for that term comes
   from: `linked_from_dictionary` means it's sourced from the existing
   psl.org.pk dictionary (linked out, not re-hosted, per ©FESF) --
   currently all 42 v1 terms are in this state, since the glossary was
   built specifically from confirmed dictionary matches. `not_recorded`
   would mean no video source exists yet at all (relevant again once
   newly-coined signs, e.g. for loop/if-else, need original video shot
   with Deaf Reach/FESF).
2. **Tokenizer** — maps a recognized PSL identifier (a sign) to a software
   token (e.g. the sign for "number" -> the token `NUMBER`).
3. **Parser / AST** — takes a stream of tokens and organizes them into an
   Abstract Syntax Tree.
4. **Code generator** — walks the AST and emits real, runnable Python
   source. Proven end-to-end: a real PSL sign sequence tokenizes, parses,
   and compiles to Python that has actually been executed and produces
   the correct output.

## Pipeline

```
PSL sign / video frame
        |
        v
   [ Tokenizer ]   ->  software tokens (NUMBER, OP_ADD, FUNCTION_DEF, ...)
        |
        v
   [ Parser ]      ->  builds an Abstract Syntax Tree (AST)
        |
        v
   [ Codegen ]     ->  Python source code, executed and verified
```

## Project layout

```
psl-compiler/
├── src/psl_compiler/
│   ├── tokenizer/     # visual identifier -> token mapping
│   ├── parser/        # token stream -> AST
│   ├── ast/           # AST node definitions
│   ├── glossary/      # term list + video metadata loader
│   └── utils/         # shared helpers
├── data/
│   ├── terms.json     # master list of 32 v1 terms
│   └── terms.csv       # same data, CSV form
├── tests/              # unit tests
└── docs/               # design notes
```

## Status

- [x] Repo + architecture (Week 1)
- [x] v1 term list, 42 terms with confirmed/candidate PSL dictionary signs (Week 1-2)
- [x] Tokenizer error handling: `UnknownIdentifierError`, safe mode, `is_known()`, `unknown_identifiers()` (Week 2)
- [x] Parser: arithmetic/comparison expressions with correct precedence, bracket grouping, print/return statements (Week 2)
- [x] Individual digit signs (one, two, three, five, seven, eight, nine, ten, twenty, hundred) wired in as real literal values -- first genuine end-to-end sign-sequence -> AST flow (Week 2)
- [x] Code generator: AST -> real Python source. Full pipeline proven end-to-end -- a real sign sequence tokenizes, parses, compiles, and *executes* with the correct output (Week 2)
- [x] Variables, if/else, and repeat loops, with indentation support and a fixed curly/square bracket distinction -- using **provisional, unverified** signs pending Deaf Reach/FESF (v2)
- [x] Top-level `return` now raises a clear error instead of generating broken Python (v2, fixes a review-flagged bug)
- [ ] Fluent-signer verification of the 9 `partial` matches AND the new provisional v2 signs (variable_a/b/c, assign, if_statement, else_statement, repeat_statement, true, false) -- none of these are real confirmed PSL signs yet
- [ ] Confirm whether signs for "four" and "six" exist (not found in the Numbers category page checked so far)
- [ ] Function definitions with real bodies (blocked: no PSL sign yet for user-defined names/identifiers)
- [ ] Lists/arrays (not yet designed or parseable)
- [ ] Student-facing click-based interface (so learners select signs, not type English identifier strings) -- this is the actual point of the project and doesn't exist yet
- [ ] Visual/rule-based error system (currently errors surface as Python exceptions/tracebacks, in English)
- [ ] Sign development with Deaf Reach / FESF for loop/if-else/boolean/array/variable (provisional placeholders exist in code now, but need real signs)

## Getting started

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

## Open design questions

- **How does a specific numeric value get expressed?** Resolved for
  small/round numbers: the PSL dictionary's Numbers category has
  individual signs for one, two, three, five, seven, eight, nine, ten,
  twenty, and hundred, each wired to a real literal value in
  `data/terms.json` (see `number_one`, `number_two`, etc.). Open gap:
  "four" and "six" weren't found in the Numbers category page checked so
  far -- confirm with Deaf Reach whether they exist elsewhere before
  assuming they need coining.
- **How would a function get a name?** `FUNCTION_DEF` exists as a token,
  but user-defined names (function names, parameters) have no PSL sign
  concept yet -- unclear if that should be fingerspelling, a separate
  identifier system, or something else entirely.
- What exactly counts as a "PSL identifier" as input -- a still image, a
  video frame, a pre-labeled dataset entry, or live camera input?
- Should the AST target real executable Python, or just a structural
  diagram/representation?
- How to close the gap on loop/if-else/boolean/array: sign development
  with Deaf Reach/FESF, or checking more of the ~35 PSL dictionary
  categories for stray matches first?
