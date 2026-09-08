# PSL Compiler

A pipeline that converts visual PSL (sign-language) identifiers for core computing
concepts into real, runnable Python code — plus a video glossary that teaches
each term, linking to existing Pakistan Sign Language (PSL) dictionary signs
wherever one already exists.

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
- [ ] Fluent-signer verification of the 9 `partial` matches
- [ ] Confirm whether signs for "four" and "six" exist (not found in the Numbers category page checked so far)
- [ ] Function definitions with real bodies (blocked: no PSL sign yet for user-defined names/identifiers)
- [ ] Known limitation: a bare `return` at the top level generates syntactically invalid standalone Python (Python requires `return` inside a function) -- needs a decision once function bodies are parseable
- [ ] Sign development with Deaf Reach / FESF for loop/if-else/boolean/array

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
