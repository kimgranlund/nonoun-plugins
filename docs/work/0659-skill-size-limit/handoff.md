---
id: T-0659
title: "Every SKILL.md stays under 18,000 characters"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every SKILL.md in both plugins stays under 18,000 characters, so a skill body the host re-injects after a compaction (capped at 20,000 characters) arrives whole, and a plugin check fails any SKILL.md over the limit.

## Intent
- Do: (1) Trim `plugins/sdlc-lite/skills/chain/SKILL.md` under 18,000 characters by moving detail (argument notes, lean-chain detail, long examples) into `skills/chain/references/` and linking it from the step that uses it. (2) Trim `skills/handoff-format/SKILL.md`, `skills/fanout/SKILL.md` and `skills/ticket/SKILL.md` the same way, into each skill's own `references/` folder. (3) `scripts/check-packaging.py` `check()` fails any `plugins/*/skills/*/SKILL.md` whose text is 18,000 characters or more, naming the file, its size and the limit.
- Non-goals: rewording or shortening the guidance itself; trimming skills already under the limit; descriptions (T-0665).
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #19, ui-kit-neue audit 2026-10-20.
The host re-injects invoked skill bodies after a compaction, capped at 20,000 characters; in the audited conductor session the chain skill lost its later sections (5 Loose ends, 6 File, 7 Close out, Report) after each of three compactions, and re-injected skill bodies cost about 20M cache_read (2.1%).
Measured here (Python `len()` of the file text, 2026-10-20): `skills/handoff-format/SKILL.md` 29,850; `skills/chain/SKILL.md` 27,335; `skills/fanout/SKILL.md` 19,857; `skills/ticket/SKILL.md` 18,496. Every other SKILL.md in both plugins is under 15,000. The issue named only chain and fanout; handoff-format and ticket are also over 18,000.
Chain headings: `plugins/sdlc-lite/skills/chain/SKILL.md:14` Arguments, `:22` Lean chain, `:35` to `:92` steps 1 to 7, `:97` Report. `skills/handoff-format/` already has a `references/` folder and `run-operations.md`; chain, fanout and ticket have none yet.
The packaging check is the right home because it already walks both plugins' skills (`scripts/check-packaging.py:38`, the frontmatter rule). It has no selftest, so the negative control runs it with `--root` on a copy of the repo.
Landmines: `plugins/sdlc-lite/scripts/check.py` pins phrases to specific SKILL.md files (for example items 6, 16 and 40 name `skills/handoff-format/SKILL.md` and `skills/chain/SKILL.md`; item 6 compares the fenced merge-step block in handoff-format with `agents/planner.md` byte for byte). Moving a pinned phrase out of SKILL.md fails `check.py`; either keep it in SKILL.md or repoint that check item to the reference file. `check.py` item 42 requires every link to stay inside its own skill folder.

## Constraints
The numbered steps and the Report heading of the chain skill stay in `skills/chain/SKILL.md`; only their detail moves. No skill frontmatter changes. Every check.py contract keeps passing.

## Acceptance criteria
1. `python3 -c "import glob; s=[(len(open(p).read()),p) for p in glob.glob('plugins/*/skills/*/SKILL.md')]; big=[x for x in s if x[0]>=18000]; print(big); raise SystemExit(1 if big else 0)"` prints `[]` and exits 0 (red before the change: it lists handoff-format, chain, fanout and ticket).
2. `python3 scripts/check-packaging.py` exits 0.
3. Negative control: `d=$(mktemp -d) && rsync -a --exclude .git ./ "$d"/ && python3 -c "print('x'*20000)" >> "$d"/plugins/sdlc-lite/skills/chain/SKILL.md && python3 scripts/check-packaging.py --root "$d"; echo rc=$?` prints a `FAIL:` line naming `chain/SKILL.md` and the 18,000 limit, and `rc=1`. The case fails with the change reverted (it prints `rc=0`).
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `python3 plugins/sdlc-lite/scripts/prompt_lint.py` exits 0.
5. `ls plugins/sdlc-lite/skills/chain/references/` lists at least one file, and `grep -n 'references/' plugins/sdlc-lite/skills/chain/SKILL.md` shows the link to it.
6. `git diff --check` exits 0.
