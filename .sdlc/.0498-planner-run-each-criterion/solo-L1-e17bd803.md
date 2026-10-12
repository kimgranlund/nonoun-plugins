<!-- role=solo level=L1 model=sonnet effort=low -->
## Output
🟢 T-0498 is done. I added the `Probe-criteria` line to `planner.md`, and the new `check.py` item went red first, then green.

I made two changes:
- **`planner.md`:** one affirmative line, under rule 14's sub-bullets, reading "Probe-criteria: run each criterion span against the nearest reference sibling or the base tree and keep a criterion only when it can exit 0 on a correct tree." I regenerated the planner-L1, L2 and L3 agent definitions and the three codex `sdlc-planner-l*.toml` files from it.
- **`scripts/check.py`:** a new check that `planner.md` and the three generated `planner-L*.md` files each carry the handle and the rule phrase. It has a negative control that removes the handle and confirms the check would flag it.

Checks:
- **Red first:** before I edited `planner.md`, `check.py` printed 8 FAIL lines, a missing handle and a missing phrase in each of four files.
- **Generation:** `claude_roles.py generate --check` and `codex_roles.py generate --check` both pass.
- **`check.py`:** it prints `ok`.
- **Prompt lint:** `prompt_lint.py` shows planner prohibitions at 40 before and after the edit, so the count did not rise. It still reports 1 warning, P-5, which was already there.

There is an untracked `.sdlc/0498-planner-run-each-criterion/skips.md` in the ticket folder. I did not create it.

The ticket is level L1, so no verifier is needed. Nothing was committed.
