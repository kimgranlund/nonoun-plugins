# Name the product SDLC Lite (T-0309)

Recorded: 2026-10-06. Lane: solo (`steps.py lane` printed `solo`, size M). Method as in [the earlier rename](rename-validation-to-reports.md): `rename_refs.py apply` for the folder, a script for prose, an allowlist for dated history.

## Decisions applied

- Prose name is `SDLC Lite`. Identifiers stay: `sdlc-lite`, `SDLC_*`, `.sdlc/`, plugin and skill names.
- "Lean SDLC", "lean SDLC" and "Sdlc Lite" became "SDLC Lite". Bare "SDLC" meaning this product became "SDLC Lite" (entry files, manifest descriptions, README title, Codex role text and the generated Codex agent descriptions). "lean lane" and the `## Lean chain` heading stay.
- `docs/lean-sdlc/` moved to `docs/sdlc-lite/` (7 files, `git mv`); 19 references in 13 files rewritten by `rename_refs.py apply docs/lean-sdlc docs/sdlc-lite` restricted to live files with `--only`, plus the folder row in `docs/AGENTS.md` and one target column in `docs/docs-schema/design.md` by hand.
- No model or effort value changed. The managed block in `onboard.py` and the router blocks in `tickets.py` contain none of the variants, so nothing was left there.

## Counts

Occurrences in tracked text files. "History" is the allowlisted set below; "live" is everything else. Before is `main` at aa1dd36; after is this branch. The inventory script was a throwaway in /tmp.

| Variant | History before | Live before | Live after |
| --- | --- | --- | --- |
| `Lean SDLC` | 5 | 8 | 2 (ticket handoff) |
| `lean SDLC` | 24 | 11 | 2 (ticket handoff) |
| `SDLC-Lite` | 0 | 0 | 1 (ticket handoff) |
| `sdlc lite` | 0 | 0 | 1 (ticket handoff) |
| `Sdlc Lite` | 0 | 1 (`.agents/plugins/marketplace.json`) | 0 |
| bare `SDLC` (product meaning) | 61 | 100 (60 of them in generated Codex agent TOML) | 11 |
| `lean-sdlc` (any use) | 219 | 49 | 30 |

Live after, by cause. The 4 spellings above sit only in the T-0309 handoff, which names them on purpose (allowlisted). The 11 bare "SDLC" are: `.sdlc/notes.md` (1, a dated note, "SDLC-caused"), `.sdlc/roadmap.md` (1, a generated closed-ticket title), the T-0309 handoff (5), the guard's own banned-string source in `check.py` (3, split literals), and the vocabulary note in `docs/sdlc-lite/README.md` (1). The 30 `lean-sdlc` are file names of dated reports (`docs/reports/lean-sdlc-design-review*.md`, `lean-sdlc-cost-control-review.md`, kept because reports are history), the T-0309 title in the ticket, generated roadmap and router, and the `.sdlc/lean-sdlc-*` workspace directory names.

## Places a variant sits inside an identifier, path, quoted dated text or managed block

- Paths: `docs/reports/lean-sdlc-*.md` (three report files and their links), `.sdlc/lean-sdlc-review*`, `.sdlc/lean-sdlc-cost-review` run workspaces. Not renamed; linked as is.
- `docs/sdlc-lite/cost-control.md` line 234 and `design.md` line 5 cite `../validation/lean-sdlc-*` (a stale link from the earlier rename, already on the broken-link allowlist). Left.
- Quoted dated text: `.sdlc/notes.md` and every `.sdlc/.NNNN-*` folder, `docs/reports/`, `plugins/sdlc-lite/bench/results/`, run workspaces `.sdlc/verify-*`. Left.
- Managed block text (`onboard.py`) and router blocks (`tickets.py`): none contain a variant.

## Allowlist for the guard

`check.py` item 34 (`NAME_ALLOW`): `docs/reports/*`, `.sdlc/.[0-9]*` (closed tickets), `.sdlc/verify-*` (verifier run workspaces), `.sdlc/*0309*` (this ticket's handoff), `plugins/sdlc-lite/bench/results/*`. Tags and published release pages are not touched; their old text and paths stay.

## Guard and checks

- Guard: `check.py` fails on `Lean SDLC`, `lean SDLC`, `SDLC-Lite` and `sdlc lite` in tracked files outside the allowlist. The banned strings in its own source are split so it does not flag itself.
- Positive case: `python3 plugins/sdlc-lite/scripts/check.py` prints `ok: 19 role levels, 9 agents checked`.
- Negative control observed: appending `planted: Lean SDLC here` to `docs/maintenance/sdlc-internals.md` made it print `FAIL check.py: product name: docs/maintenance/sdlc-internals.md: retired spelling "Lean SDLC"` and exit 1; after `git checkout` of the file it printed `ok` again. The check also carries two in-process controls (a planted spelling is flagged, an allowlisted path is not).
- Broken relative Markdown links (`rename_refs.py links`): 12 before, 12 after (797 checked, same targets; the baseline allowlist test inside `check.py` agrees).
- `codex_roles.py generate` rewrote the generated agent TOML; `generate --check` verified. `check-packaging.py` PASS. `tickets.py check` ok.

Verification by the independent verifier and the full suite run are recorded in the ticket's close reason.
