<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
fail

## Criteria
- `grep -q '"scout": {"L1": \["gpt-6-luna", "high"\]}' plugins/sdlc-lite/adapters/codex/models.json`: pass. Evidence: exit 0 on the built tree and exit 1 in a throwaway worktree at `$SDLC_BASE_SHA` 69ba9eb, so the check bites. `git diff` shows that one line is the only change in models.json.
- `grep -q "gpt-6-luna" plugins/sdlc-lite/adapters/codex/agents/sdlc-scout-l1.toml`: pass. Evidence: exit 0 on the built tree and exit 1 at base. The diff changes `model = "gpt-6-astra"` to `model = "gpt-6-luna"` and nothing else.
- `grep -q "returned scout L1 to" docs/codex-role-execution.md`: pass. Evidence: exit 0 on the built tree and exit 1 at base. docs/codex-role-execution.md:43 has the new sentence, placed after the `gpt-6.1-sol` alternate sentence as the Do requires. The replacement sentence "the scout was briefly moved to `gpt-6-astra` on the strength of those 0.154.0 probes." is there verbatim, and the link is unchanged.
- `! grep -q "was the only accepted model in the probes" docs/codex-role-execution.md`: pass. Evidence: exit 0 on the built tree and exit 1 at base, where the phrase is present. The file path exists, so the negation is not vacuous.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: "Codex agent definitions verified", exit 0 on both the built tree and base. Negative control: in a throwaway worktree at HEAD I copied in the new models.json without regenerating, and the check exited non-zero with "generated agent drift: .../sdlc-scout-l1.toml".
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: pass. Evidence: exit 0 on the built tree ("Installed 22 project agents ..." lines) and exit 0 at base. This settles the exit code the builder said it could not confirm.

## Out of scope changes
None. `git status` shows only the three files the Do names, plus the untracked `.sdlc/codex-scout-luna/` run artifacts. `git diff --check` is clean.

## For the next attempt
plan defect: the step changed a shared contract (the scout L1 model in `adapters/codex/models.json`) but did not include its dependent doc table. `docs/codex-role-execution.md:37`, under "## Default model mapping", still reads `| Scout | Astra high | | | | |`. It now contradicts models.json and the new note at line 43.

`git log -L37,37:docs/codex-role-execution.md` shows the table follows models.json:
- 7f0fafc wrote `Luna high`.
- 69ba9eb changed it to `Astra high` with the earlier model move.

Steelman: the builder would answer that the Do limited the docs edit to the 2026-09-29 note. It did, so this is not a builder defect. The replan needs to widen step 1's Do with this edit: change `docs/codex-role-execution.md:37` to `| Scout | Luna high | | | | |`. It also needs a criterion that bites, for example `grep -q '^| Scout | Luna high |' docs/codex-role-execution.md`, which is red on the current tree.

No criterion swap is proposed, because the build itself still needs this change. The remaining build work is correct as it stands.

I left the dated validation records alone because they are historical records the user contract says stay as dated reports: `docs/reports/codex-account-models-2026-09-30.md:55` ("including scout L1 Astra high") and `docs/reports/release-0.19.0.md:22`.
