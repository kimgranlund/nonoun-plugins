<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 Done when: `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with a case where step 2 cites a path step 1 marks as created (lint ok) and a negative control where the same path has no create marker (refused as before): pass. Evidence: the selftest printed `steps selftest: PASS` and exited 0. It printed `ok: (r) T-0533: a path an earlier step marks [creates:] passes lint, split --only, and step lint` and `ok: (r) T-0533 control: with no create marker lint, split --only, and step lint still refuse`. The positive case covers `lint <task dir>`, `split --only 2` and the live `step-2` handoff lint; the control asserts rc 1 and the missing path named in all three. Observed red: in a throwaway worktree at HEAD I removed the `earlier_created` merge in `link_findings` and the `covered_by(rel, created)` guard in `lint_steps`. The selftest then printed `steps selftest: FAIL ... - (r) T-0533: a path an earlier step marks [creates:] passes lint, split --only, and step lint`, while the control stayed ok. Both checks can therefore go red.
- Intent "keep the existing refusal for a path no step creates and the tree lacks": pass. Evidence: the control case above; the rest of the steps selftest (including the existing `gone/AGENTS.md` refusal and the `.sdlc` link cases) is unchanged and green.
- Intent "apply the same rule in `split --only N`": pass. Evidence: `rc2` in the new selftest case runs `split <dir> --only 2` and is 0 with the marker and 1 without.

Neighbors checked, all green: `codex_roles.py generate --check` (Codex agent definitions verified), `claude_roles.py generate --check` (23 files), `scripts/check-packaging.py` (PASS), `prompt_lint.py selftest` (PASS), `plan_check.py selftest` (PASS, 333 checks), `git diff --check 3509ed11` (clean).

## Out of scope changes
None. The diff against 3509ed11 is `steps.py` (the code, its usage text and the selftest), the four planner role files (`planner.md` and `planner-L1.md`, `-L2.md` and `-L3.md`) plus the three regenerated Codex planner TOMLs, the `handoff-format` SKILL.md sentence, and the run records in the task folder. All of it documents or generates the one rule.

## For the next attempt
None.

## Notes
- The ticket's Context asks the result to say whether the T-0520 case (paths outside the repo tree, described in prose) needs the same rule or a separate one. The solo report (`solo-L2-ff5862b6.md`) holds only the usage-limit message, so no answer was recorded. From the diff: the existing `Other repo: <name>` line and absolute-outside-repo rules in `is_foreign_citation` were left unchanged, and the new rule only covers paths an earlier step declares created. Whoever closes the ticket should state "separate rule, already covered by the foreign-path exemption when declared" or file a follow-up.
- `.sdlc/0533-split-lint-creates-marker/base-sha` is untracked, a lane-driver artifact.
