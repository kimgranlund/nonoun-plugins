# Notes

`tickets.py close` appends follow-ups that did not become tickets.

## T-0105: Find out why the T-0072 background hook did not stop the run in... (2026-09-26)

- note: the Monitor tool name in the `PreToolUse` payload is assumed to be exactly `"Monitor"` (matching the hooks.json matcher and block-background.sh's check); no live probe covers it, same as the planner's Risks and the T-0076 non-goal it inherits.
- note: step 7's builder accidentally ran `git checkout` on `run.sh` mid-mutation-test, discarding its uncommitted steps 1-6 changes, and restored it from a manual `/tmp` backup taken before the mutation; the verifier independently confirmed the restore was exact (matching diff stats and intact heading-pick and timeout-floor lines), but the near-loss is worth knowing about if this pattern recurs.

## T-0160: Onboard skill: entry files, docs layout, and check mode (2026-09-29)

- decide: The house linter `skill_lint.py` flags F2 (`disable-model-invocation` and `user-invocable` not declared) and W2 (no "Use when" phrasing) on the `onboard` and `progressive-context` skills, and no repo or host skill validator has run on either; decide whether to adopt those rules.
- note: The step 4 and step 5 builders and the step 4 verifier left throwaway projects in the OS temp folder, because `rm -rf` was denied.
- note: The design's "Unsettled" items are not covered by any artifact: whether an installed plugin can read its own template version on both hosts, and the token cost of nested entries in a real role run.
- note: The selftest's `digest()` mutant survives, since the gates only compare marker and text with each other; the real hashes were confirmed once by `shasum`, not by a gate.

## T-0161: Spike: read-only reorganization plan on this repository (2026-09-29)

- decide: Whether to build apply for the reorganization or drop it. The spike recommends deferring, since a reviewed plan is 2 moves and 13 line edits by hand. Revisit only when a repository's plan is too large to carry out by hand.
- decide: Whether to update `docs/repo-onboarding/reorganization.md` to v0.7 with the "Rules to change" list (plan file outside `.sdlc/`, the `Date:` frozen-candidate test, the added plan fields, regenerate and compare for N15).
- fix-now: Freeze `docs/claude-handoff.md` and `docs/claude-response.md` in a real `docs/layout.md` before any reorganization of this repository uses the plan.
- note: The two-sources-one-destination collision code path in `reorg_plan.py` was never exercised on this tree.
- note: A broad glob such as `claude-*.md` pulls the placed file `docs/maintenance/claude-hooks.md`, so the design's glob rules need a warning for it.
