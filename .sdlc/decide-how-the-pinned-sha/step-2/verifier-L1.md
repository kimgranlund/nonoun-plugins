<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep '^6\. ' plugins/sdlc-lite/agents/planner.md | grep -q 'merge-base --is-ancestor'`: pass. Evidence: exit 0 on the built tree (c1=0). In a throwaway worktree at `$SDLC_BASE_SHA` 86d3f5d it exits 1 (c1=1), and exactly one line matches `^6\. ` there, so the check can go red. Diff: rule 6 now ends "...as a `plan defect`, except the deliberate ancestry form `git merge-base --is-ancestor <sha> HEAD`, which passes."
- `grep -F 'scripts/steps.py' CLAUDE.md | grep -q 'is-ancestor'`: pass. Evidence: exit 0 on the built tree (c2=0) and exit 1 at base (c2=1). Diff: the parenthetical becomes "compare against `HEAD` instead, except the deliberate ancestry form `git merge-base --is-ancestor <sha> HEAD`, which passes)".
- `grep -F 'pins a commit sha' .claude/agents/sdlc-lite-author.md | grep -q 'is-ancestor'`: pass. Evidence: exit 0 on the built tree (c3=0) and exit 1 at base (c3=1), where one line matches. Diff: "fixed at plan time (except the deliberate ancestry form `git merge-base --is-ancestor <sha> HEAD`, which passes)". The wording is identical in all three docs, as the Do asks.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0 on the built tree, ending with "ok: shellcheck", "ok: plugin validate", and the order, fanout, run, hook, and hook live probe selftests all PASS. None of the 23 "fail" substring hits is a non-`ok` line, so none is a failure. The guard bites: in the base worktree I changed CLAUDE.md builder L1 to Haiku and check.sh exited 1 with "FAIL CLAUDE.md: builder:L1 = Haiku low, run.sh = Sonnet low".

## Out of scope changes
None. `git diff --name-only "$SDLC_BASE_SHA"` lists five files. Three of them are this step's docs. `plugins/sdlc-lite/scripts/steps.py` is step 1's exemption code. `.sdlc/decide-how-the-pinned-sha/handoff.md` is the task handoff, which the conductor updates, not the builder, and it is 5 lines. check.sh is green over all of it. Steelman on a possible finding that the docs do not say "a span that also holds another sha is still refused": that is Do prose, and no criterion asks for that wording. "Every other pinned sha" is covered by the doc text "the one allowed form", read as "which passes" only for that form. I dropped it.

## For the next attempt
None
