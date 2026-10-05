# Rename docs/validation to docs/reports (T-0246)

Recorded: 2026-10-05. Tool: `plugins/sdlc-lite/scripts/rename_refs.py` (`plan`, `apply`, `check`, `links`, `selftest`).

## Before and after

| Measure | Before | After |
| --- | --- | --- |
| Tracked files under the evidence folder | 402 under `docs/validation/` | 403 under `docs/reports/` (the 402 plus `readiness-recovery-validation.md`) |
| Tracked files outside the folder citing `docs/validation` | 355 | 0 outside the allowlist |
| Tracked files citing it anywhere | 388 | 0 outside the allowlist |
| Occurrences of the string | 1355 | 0 outside the allowlist |
| Broken relative Markdown links (tracked `.md`, 826 checked) | 95 | 95 (all 95 pre-existing, same targets; one link the move itself broke was fixed by hand) |

The rewrite changed 402 files and 1833 references (path tokens and recomputed relative links, anchors kept).

## Rules the tool applies

A path token starts at the beginning of text or after whitespace, a quote, a backtick, a paren, a bracket, `=`, `|`, `!`, `*` or `/`. It is not rewritten inside a URL, after `:` (text bound to a tag such as `v0.20.7:docs/validation/x.md`), or when the old path is a prefix of a longer name. Relative links are resolved from the file's folder, rewritten, and recomputed; anchors survive.

## Allowlist for the stale-reference check

- `.sdlc/0246-*`: this ticket's handoff, which names the old path on purpose.
- `docs/repo-onboarding/reorganization.md` and this note: sentences that are about the rename.

`rename_refs.py check docs/validation --allow ...` reports 0 stale references. `rename_refs.py selftest` includes a negative control: a reintroduced stale reference in a fixture is found, and the allowlist suppresses it.

## Limits

- Tags `v0.20.0` to `v0.20.8` keep `docs/validation/...` paths, and the published GitHub release bodies for 0.20.1 to 0.20.8 are not edited. Their links resolve only at the tag. The next release record says so.
- The tool does not parse every Markdown form (for example reference links across lines or HTML `href`); the link count above shows no new breakage in the forms it checks.
