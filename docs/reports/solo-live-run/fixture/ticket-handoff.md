---
id: T-0001
title: "slugify max_length that cuts at a word boundary"
type: feature
status: ready
size: M
priority: P2
depends: []
created: 2026-10-04
---

## Goal
`slugify` takes an optional `max_length` and never returns a slug longer than it, cutting at a word boundary.

## Intent
- Do:
  - Add a helper `truncate_at_boundary(slug, max_length, sep)` in `strkit/words.py` and export it from `strkit/__init__.py` (add it to `__all__`).
    - If `len(slug) <= max_length`, return `slug` unchanged.
    - Else return the longest prefix of whole `sep`-separated words whose length is at most `max_length`, with no trailing `sep`.
    - If even the first word is longer than `max_length`, return the first `max_length` characters of `slug`.
    - `max_length` below 1 raises `ValueError`.
  - Add a keyword parameter `max_length=None` to `slugify(text, sep='-', max_length=None)` in `strkit/slug.py`. `None` keeps today's behavior. Any other value applies `truncate_at_boundary` to the slug with the same `sep`, so `max_length` below 1 raises `ValueError` even for empty text.
  - Add tests for the new behavior to `tests/test_slug.py` and document `max_length` and `truncate_at_boundary` in `README.md`.
- Non-goals: any other change to `slugify` or `split_words`; new dependencies.
- Done when: the behavior above holds and `python3 -m unittest discover -s tests` passes.

## Context
Example: `slugify('Hello World Again', max_length=12)` is `'hello-world'`, and `slugify('Supercalifragilistic word', max_length=5)` is `'super'`.
