## Goal
Conductors refresh the managed blocks of their own repo's docs entry files without waiting for the maintainer, under one written narrow rule.

## Intent
Literal ask: conductors may refresh the managed blocks of docs/*/AGENTS.md in their own repo without waiting for the maintainer, under a written narrow rule, and nothing broader.
Deltas:
- where the rule lives: (gap: which file conductors read the onboard rule from; default: the onboard skill holds the rule once and the conductor text links it)
- what counts as narrow: defaulted: run setup only when the dry run touches nothing but managed blocks in docs entry files of the same repo
Do: write the rule once in the onboard skill (check, dry run, then setup only for a managed-block-only diff) and link it from the conductor text.
Level: L1 (lane: solo; cost: low, two text edits; reversible: yes)
Non-goals: any change to onboard.py behavior; model or effort changes.
Done when:
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py` exits 0
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/docs_check.py` exits 0
