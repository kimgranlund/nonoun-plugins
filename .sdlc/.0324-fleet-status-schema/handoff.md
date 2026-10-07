---
id: T-0324
title: "JSON schema for the fleet_status collect output, and render as one plain aligned CLI table per section"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0323]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The per-repo status that `fleet_status.py collect` emits is pinned by a JSON schema file, and `render` shows it as simple aligned CLI tables (plain columns, one state emoji column), nothing fancier.

## Intent
- Do: (1) Add `plugins/sdlc-lite/skills/fleet-status/resources/fleet-status.schema.json` (shipped with the skill; the SKILL.md links it, and guard 37 in check.py pins that the file exists and parses as JSON) (JSON Schema, draft 2020-12) describing the `collect` object (machine, repos with rows, needs_you, release, delta). The key list already lives in the docstring of plugins/sdlc-lite/scripts/fleet_status.py; make the schema the authority and point the docstring at it. (2) Make `fleet_status.py selftest` validate a collected fixture against the schema using only the standard library (a small checker for the keywords the schema uses; no new dependency) with a negative control (a fixture missing a required key must be rejected). (3) After T-0323 lands, render each section as a plain table: header row, aligned columns padded with spaces, a dashed rule, no markdown pipes, state shown by the colored emoji. If T-0323 chose markdown pipe tables, replace them with this plain form.
- Non-goals: new data fields, the stop line, the skill's AskUserQuestion step, any new dependency.
- Done when:
  - `fleet_status.py collect` output validates against the schema in selftest (observed), and the negative control fails on a missing key.
  - `fleet_status.py render --no-write --no-gh` prints aligned plain tables with no pipes and no em dash.
  - `check.py`, `tickets.py check`, and the fleet_status selftest pass; docs/references/sdlc-internals.md names the schema.

## Context
User direction on 2026-10-06: capture each repo's status in a JSON schema or similar, and show the contents in a simple CLI table. Depends on T-0323 (colored marks, collapse of done-but-open rows).

## Constraints
No em or en dashes. No push or publish. Model and effort defaults unchanged.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 -c "import json; json.load(open('plugins/sdlc-lite/skills/fleet-status/resources/fleet-status.schema.json', encoding='utf-8'))"`
- `python3 plugins/sdlc-lite/scripts/fleet_status.py collect --no-gh --no-write 2>/dev/null | python3 -c "import sys, json; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import fleet_status as f; e = f.schema_errors(json.load(sys.stdin), f.load_schema()); print(e); sys.exit(1 if e else 0)"`
- (guard) `python3 plugins/sdlc-lite/scripts/fleet_status.py collect --no-gh --no-write 2>/dev/null | python3 -c "import sys, json; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import fleet_status as f; d = json.load(sys.stdin); del d['delta']; e = f.schema_errors(d, f.load_schema()); print(e); sys.exit(0 if e else 1)"`
- `python3 plugins/sdlc-lite/scripts/fleet_status.py render --no-write --no-gh | python3 -c "import sys; t = sys.stdin.read(); sys.exit(0 if ('|' not in t and chr(0x2014) not in t and chr(0x2013) not in t and 'Repo' in t and '-----' in t) else 1)"`
- `grep -q 'fleet-status.schema.json' docs/references/sdlc-internals.md`
- `grep -q 'resources/fleet-status.schema.json' plugins/sdlc-lite/skills/fleet-status/SKILL.md`
- `git diff --check`

## Closed

2026-10-06: delivered by the solo agent (tier M); one independent batched verifier passed before the merge
