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

## T-0162: Planner names the entry files each step needs (2026-09-29)

- note: `check.sh` skipped shellcheck (not installed), so the shell-lint part of the release gate was not run for this change.
- note: The Codex live run put builder and verifier on one model (`gpt-6-astra`, `shared_with_builder=yes`), so it does not show independent verification on Codex.
- note: In the live run, the Codex reads were combined `cat` commands, and the report records that the evidence is the read, not rule compliance.

## T-0163: Codex rejects gpt-6-sol and gpt-6-luna on a ChatGPT account (2026-09-29)

- decide: Scout L1 still uses `gpt-6-luna`, which a ChatGPT account rejects, so Codex scout runs fail there until the user picks a replacement or accepts it.
- decide: No live `scripts/run.sh` run with the Codex backend on a ChatGPT account was made. The root AGENTS.md asks for a focused live run in a throwaway project for changed role behavior.
- note: `docs/validation/native-codex-smoke.json` hashes the deleted alternate TOMLs. It was left as historical evidence, and it may look stale next to the current agent set.
- note: Projects that installed the old agents keep stale `sdlc-verifier-lN-alternate` TOMLs in `.codex/agents/`, because `install` does not remove files it no longer generates. They are unused while no alternate is configured.
