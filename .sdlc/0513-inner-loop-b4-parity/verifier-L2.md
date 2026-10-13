## Verdict
pass

## Criteria
- #1 `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 and its `(parity)` cases hold, with the two refusals red before `parity_findings` existed: pass. Evidence: in the tree, `steps.py selftest` gave rc=0 and printed `steps selftest: PASS` with four parity lines: `ok: (parity) a capture command, two image paths and a property list lint clean`, `ok: (parity) a line with one image path is refused`, `ok: (parity) a line with no property list is refused`, and `ok: (parity) control: a line without the (parity) tag is not checked`. For the negative control I copied the tree to /tmp and put `return []` at the top of `parity_findings` (plugins/sdlc-lite/scripts/steps.py:1707). Selftest then gave rc=1 and listed `- (parity) a line with one image path is refused` and `- (parity) a line with no property list is refused` as misses, while the accepted form and the untagged control stayed ok. Both refusal cases also assert `'plan defect' in err` (steps.py:6156-6159). No process-deviations.md exists.
- #2 `python3 plugins/sdlc-lite/scripts/check.py` exits 0, including the `verifier parity` item, seen red with one phrase removed from `verifier-L1.md`: pass. Evidence: `check.py` in the tree gave rc=0 with `ok: 19 role levels, 9 agents, 22 generated definitions checked`. The item is at check.py:1403-1410. On a /tmp copy of the tree, swapping `Read the real and the mockup image` out of agents/verifier-L1.md gave rc=1 with `FAIL check.py: verifier parity: agents/verifier-L1.md missing "Read the real and the mockup image"`. Swapping out the other phrase gave rc=1 with `FAIL check.py: verifier parity: agents/verifier-L1.md missing "a \`(parity)\` criterion passes per named property"`. The unmodified copy's only failure was the uncopied `.claude/agents/sdlc-lite-author.md` (an artifact of the copy), so each red message comes from the parity item.
- #3 `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0: pass. Evidence: rc=0, `Claude agent definitions verified (22 files)`. Negative control: in the /tmp copy, putting back the base agents/verifier-L1.md printed `claude_roles.py: differs from the level table and role file: agents/verifier-L1.md` and `Claude agent definitions are stale`.
- #4 `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0: pass. Evidence: rc=0, `Codex agent definitions verified`. Negative control: in the /tmp copy, putting back the base adapters/codex/agents/sdlc-verifier-l1.toml printed `generated agent drift: .../sdlc-verifier-l1.toml`.
- #5 the two `grep -q` checks on verifier.md and handoff-format/SKILL.md exit 0: pass. Evidence: in the tree, g1=0 and g2=0 (plugins/sdlc-lite/agents/verifier.md:33, plugins/sdlc-lite/skills/handoff-format/SKILL.md:174). In a `git archive 07a5c289` extract, both greps returned 1, so the check bites. The paths are full, so this is not the vacuous missing-path form.

## Out of scope changes
None. `git diff --stat 07a5c289` shows these changes:
- verifier.md and its L1/L2/L3 files: the one Intent line plus regenerated copies.
- Six Codex verifier TOMLs: regenerated, and each diff touches only `developer_instructions`.
- check.py: item 59.
- steps.py: `parity_findings`, its usage text, and the selftest cases.
- handoff-format/SKILL.md: the documented form.
- The ticket handoff.md: the `## Acceptance criteria` section was added. The solo lane wrote it, and the user did not write it. It does not conflict with the Intent's Done-when.

The untracked base-sha, skips.md and the verifier dispatch/attempt JSON files are run records. Neighbors: `git diff --check 07a5c289` gave rc=0, and `python3 scripts/check-packaging.py` gave rc=0. The verifier.md line contains no "never" or "do not", so it adds no new prohibition and keeps the Constraint.

## For the next attempt
None

## Notes
- The hook block-stray-worktree.sh blocked creating a throwaway worktree because SDLC_TMP_WORKTREES was unset ("role 'solo'"). Base and negative-control runs used a `git archive 07a5c289` extract and a file copy under /tmp/v0513.xyFG instead. Permission to remove that directory afterwards was denied, so it remains outside the repo.
- plugins/sdlc-lite/scripts/steps.py:1707: lint does not enforce the "at most five properties" or the never-"matches" part of the form. Only the documentation and the verifier line carry them. The Intent asks lint to refuse only the missing-paths and missing-property-list cases, so this is no criterion gap.
