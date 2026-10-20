---
id: T-0663
title: "onboard creates the docs folder routers that docs/AGENTS.md links"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The onboard-managed `docs/AGENTS.md` never links a folder router that onboard does not write, and its "Adding a document" step says where a link goes when the folder has no router.

## Intent
- Do: (1) In `plugins/sdlc-lite/scripts/onboard.py`, a home whose entry file onboard will not write (a frozen home, such as the default `docs/reports/`) gets the plain folder line in the docs Contents, not a link to `<home>/AGENTS.md`: make `build_model` or `render_templates` agree with the frozen filter in `plan`. (2) Rewrite step 3 of `DOCS_AGENTS_TEMPLATE` ("Add a link to it in its folder's `AGENTS.md` ... The onboard setup also lists it") so it is true for a folder with no router: link it from the folder's `AGENTS.md` when one exists, otherwise onboard lists it in `docs/AGENTS.md` Contents. (3) Refresh this repo's `docs/AGENTS.md` with `onboard.py setup` and add an `onboard.py selftest` case for (1).
- Non-goals: creating routers for frozen homes; changing `ENTRY_THRESHOLD`; changing the D-10 rule level.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #23, ui-kit-neue audit 2026-10-20.
In the audited repo `docs/AGENTS.md` linked `[specs/](specs/AGENTS.md)` and `[reports/](reports/AGENTS.md)`, neither file existed, and an agent's `cat docs/specs/AGENTS.md` failed. Specs were reached only through ticket Context lines (design docs opened by 24 to 26 agents each), never through a router.
Confirmed here: onboard does write a home router when the home holds `ENTRY_THRESHOLD` (2, `plugins/sdlc-lite/scripts/onboard.py:570`) or more documents (`_nested_topics`, `:797`), and Contents links it (`render_templates`, `:660` to `:665`). So the specs case is fixed when specs holds two or more files. The reports case is not: `plan` drops frozen targets before writing (`:1060`), but `build_model` (`:736`) still marks the home as having an entry, so Contents links a file that is never written. Repro on a throwaway repo with two files under `docs/reports/` and the default layout (which freezes `docs/reports/`, see the selftest at `:1454`): `onboard.py setup --init` writes `- [reports/](reports/AGENTS.md)` into `docs/AGENTS.md`, no `docs/reports/AGENTS.md` exists, and `docs_check.py` prints `warning D-10 docs/AGENTS.md: link does not resolve: reports/AGENTS.md`. The existing selftest `gate_nested_entries` (`:1505`) asserts `docs/reports/AGENTS.md` is not created but never checks the Contents link.
The docs_check half of the issue already holds: D-10 warns on any Markdown link that does not resolve (`plugins/sdlc-lite/scripts/docs_check.py:350` to `:364`, selftest case at `:912`). Step 3 text: `onboard.py:477`, mirrored in this repo's `docs/AGENTS.md:55`.

## Constraints
Homes with a written router keep their link. Changing the managed block text changes its stamp, so refresh this repo's `docs/AGENTS.md` in the same change. `onboard.py check` already exits 1 on this repo for unrelated reasons (unmanaged `AGENTS.md`, `docs/goals/` and `docs/kpi/` entries, size notes); leave those alone.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0, with a new case: a fixture with two files under a frozen `docs/reports/` renders `docs/AGENTS.md` Contents without `reports/AGENTS.md`. The case fails with the change reverted.
2. `R=$(pwd) && d=$(mktemp -d) && cd "$d" && git init -q && mkdir -p docs/reports && echo '# a' > docs/reports/2026-10-01-a.md && echo '# b' > docs/reports/2026-10-01-b.md && git add -A && git -c user.name=t -c user.email=t@t commit -qm i && python3 "$R"/plugins/sdlc-lite/scripts/onboard.py setup --init >/dev/null && python3 "$R"/plugins/sdlc-lite/scripts/docs_check.py | grep -c 'D-10'` prints 0 (red before the change: 1).
3. `grep -n 'The onboard setup also lists it' plugins/sdlc-lite/scripts/onboard.py docs/AGENTS.md` finds nothing, and step 3 in `onboard.py` names the `docs/AGENTS.md` Contents fallback.
4. `python3 plugins/sdlc-lite/scripts/onboard.py check 2>&1 | grep 'docs/AGENTS.md'` prints `current docs/AGENTS.md`, and `python3 plugins/sdlc-lite/scripts/docs_check.py selftest` exits 0.
5. `git diff --check` exits 0.

## Outcome
- `plugins/sdlc-lite/scripts/onboard.py`: `build_model` marks a home as having an entry only when its `AGENTS.md` is not frozen or already exists, so Contents shows the plain folder line for a frozen home with no router (this repo's hand-written `docs/reports/AGENTS.md` keeps its link). Step 3 of `DOCS_AGENTS_TEMPLATE` now names the `docs/AGENTS.md` Contents fallback.
- Selftest: `gate_nested_entries` asserts the frozen `reports/` home renders as `` `reports/` `` with no `reports/AGENTS.md` link; new negative variant `links the entry of a frozen home`. With the fix reverted the gate fails (`docs/AGENTS.md links the entry of the frozen reports/ home`).
- `docs/AGENTS.md` refreshed with `onboard.py setup` (step 3 text and stamp).
- Criteria: 1 exit 0; 2 prints 0; 3 grep finds nothing; 4 prints `current docs/AGENTS.md`, docs_check selftest exit 0; 5 exit 0. Repo `docs_check.py` D-10 count unchanged (72, same as main).

## Outcome

2026-10-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: `redck.py deviations` printed no process deviation lines. I did not run the full `check.sh`, per the brief.) · verifier: verifier-L2 (sonnet) · base: a417e2b46f62
- Changed: see commits
- Commits: 266e06c T-0663: onboard creates the docs folder routers that docs/AGENTS.md links
- Check: 1 `onboard.py selftest` exits 0 with a new frozen-reports case that fails when the change is reverted: pass
- Check: 2 The repro prints 0 D-10 warnings: pass
- Check: 3 The old step 3 text is gone and the new step 3 names the Contents fallback: pass
- Check: 4 `check` prints `current docs/AGENTS.md` and `docs_check.py selftest` exits 0: pass
- Check: 5 `git diff --check` exits 0: pass
