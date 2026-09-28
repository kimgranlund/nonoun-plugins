<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
No plan, builder, or verifier ran for this ticket. The conductor made the edit itself, so no verifier verdict exists. The only evidence is the conductor's own note in the handoff: a grep for the stale phrase and `scripts/check.sh` exiting 0. Nothing independent confirms it.

## PR title
T-0078: Fix stale block-publish SDLC_ROLE wording in skills/file/SKILL.md

## PR body
### Summary
Step 4 of `skills/file/SKILL.md` said `hooks/block-publish.sh` "only fires when `SDLC_ROLE` is set by `scripts/run.sh`". That is stale, because `scripts/fanout.py` also sets `SDLC_ROLE=conductor` for lane drivers (T-0065). This corrects the sentence. Follow-up from T-0065.

### Changes
- `plugins/sdlc-lite/skills/file/SKILL.md`, step 4: the clause now reads "since it only fires when `SDLC_ROLE` is set (by `scripts/run.sh` per role run, and by `scripts/fanout.py` as `conductor` for lane drivers)". This matches CLAUDE.md and the conductor prompt.

### Verification
- The conductor grepped agents, skills, hooks, CLAUDE.md and .claude and found no other copy of the stale phrase.
- `scripts/check.sh` exited 0.
- No plan, builder or verifier runs. The conductor made this trivial edit, so there is no independent verification.

## Changelog entry
- Fixed: `/file` skill step 4 now says the publish-blocking hook fires when `SDLC_ROLE` is set by `run.sh` (per role run) or by `fanout.py` (as `conductor`, for lane drivers).

## Follow-ups
None
