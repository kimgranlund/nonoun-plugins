# updates-log

One folder per change set to this skill: `YYYYMMDD-<slug>/changelog.md`. `CHANGELOG.md` indexes them newest first: add the new row at the top of its table in the same change. Never rewrite a past entry; a correction is a new entry that cites the old one.

## changelog.md format

Front matter first, then four sections: Added, Changed, Fixed, Open.

```yaml
---
date: YYYY-MM-DD
slug: <same as the folder suffix>
requested_by: <person who asked>
harness: <CLI or app that ran the work, e.g. Claude Code CLI 2.1.x, Codex CLI>
authors:
  - role: <conductor | solo | verifier | human>
    agent: <agent name or type>
    model: <model id>
    did: <one line: which files or steps this author changed>
project: <repo or context the work came from>
verification: <independent verifier verdict, or "none">
backup: <path of the pre-change copy, or "none">
---
```

## Rules
- The one allowed edit to a past entry: an Open line may gain a trailing "Applied in <slug>." sentence (or a ruled-out pointer to the entry that says why); nothing else changes.
- Facts only: what changed, which files, how it was checked. Cite paths, not prose from other files.
- Every agent that edited files is listed under `authors`, including the conductor for direct edits.
- No em dashes.
