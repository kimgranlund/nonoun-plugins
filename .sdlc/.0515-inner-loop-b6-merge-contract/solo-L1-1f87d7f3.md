<!-- role=solo level=L1 model=sonnet effort=low -->
## Output
T-0515 is delivered. `check.py` now fails when the conductor, fanout skill or `run-operations.md` lacks either PR merge invariant. It exited 0 after the text went in. Level is L1, so there is no verifier (`verify: none`).

Files changed:
- `plugins/sdlc-lite/agents/conductor.md`: new `PR merge:` line under `## Merge ops`.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: same `PR merge:` paragraph, placed before the `lanes.py sweep --apply` step.
- `plugins/sdlc-lite/skills/handoff-format/run-operations.md`: new step 5; Release and Never push renumbered to 6 and 7.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`: regenerated.
- `plugins/sdlc-lite/scripts/check.py`: two phrases added to `MERGE_OPS_PHRASES`, so the existing merge-ops agreement check and its negative controls cover both invariants.
- `.sdlc/.0498-planner-run-each-criterion/handoff.md`: added the agent-ui evidence line (C6, 45 minutes).

The new text says (a) the head contains the base tip (`git merge-base --is-ancestor origin/main HEAD`), (b) the gates ran at that head and none is pending (`gh pr checks <n> --watch --fail-fast`), the plugin ships no PR merge script, and `settle --forward` keeps both for the local path.

Checks:
- `check.py` red first: after adding the two phrases, it printed 4 FAIL lines for the fanout skill and `run-operations.md`. Only the `check.py` edit was in place at that point.
- `check.py` after the doc edits: exit 0.
- `claude_roles.py generate --check`: exit 0.
- `codex_roles.py generate`: ran and rewrote the conductor TOML. I did not run its `--check`.
- `prompt_lint.py`: exit 0, and `conductor.md` only gets the usual `info P-6` line, so it is not raised.

Nothing is committed. Two things are still open:
- An untracked `skips.md` appeared in the ticket folder; I did not create or inspect it.
- I did not run `specgate.py red`. The ticket's done-when has no `(red)` span, so red was shown by hand as above.
