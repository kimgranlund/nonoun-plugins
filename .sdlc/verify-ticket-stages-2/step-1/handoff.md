## Task goal
Independent check that branch `ticket-stages-mailbox` (T-0175 opt-in tickets root and router, T-0177 mailbox core, T-0178 messenger agent, T-0179 entry files and live validation) is fit to merge into main, with versions unchanged.

## Step 1: Branch check
level: L3

### Do
Verify the branch as a whole against `main`. Read `docs/ticket-stages/design.md`, the four ticket handoffs (closed folders `.sdlc/.0175-*`, `.sdlc/.0177-*`, `.sdlc/.0178-*`, `.sdlc/.0179-*`), `plugins/sdlc-lite/scripts/messages.py`, the router code in `plugins/sdlc-lite/scripts/tickets.py`, `plugins/sdlc-lite/agents/messenger.md` with its generated Codex agent, and the dated validation docs `docs/reports/messages-live-run.md` and `docs/reports/ticket-root-router-live-run.md`. Check each requirement recorded in the ticket handoffs against the code and the evidence, in particular: the message schema (required fields including follow_up_requested and protocol, optional ack_time), the transition table and folder lifecycle, that stamps are set only at their transition and are not caller-writable, the follow_up_requested gate on read to done, the two-reader race, the run.sh count notice, the router regeneration and what makes check fail, that no new skill was added, that the messenger is a declared agent and not a run.sh role, and that no version was bumped. Run the live evidence yourself where it is cheap, or report it unverified with the reason. Inject at least two defects in a throwaway worktree under SDLC_TMP_WORKTREES (for example stamp read_time at send in messages.py; leave the router count unchanged after a close) and show that a selftest or check fails for each; state what you injected and what failed. A first pass of this check (`.sdlc/verify-ticket-stages/step-1/verifier-L3.md`) failed on a stale `.sdlc/AGENTS.md` router block and on an em dash guard that counted two regenerated lines carrying text already on main; the router was regenerated with the branch's `tickets.py`, stale doc lines were fixed, and two selftest controls (`protocol`, `follow_up_requested` value checks) were added in `.sdlc/fix-protocol-controls`. Confirm each of those fixes, and check that no other closed ticket left the router stale. Report any requirement you could not verify as unverified. Write no repo files other than your result.

### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/messages.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff main --name-only -- plugins/sdlc-lite/.claude-plugin plugins/sdlc-lite/.codex-plugin plugins/progressive-context | { ! grep -q .; }`
- (guard) `git diff --check main -- . ":(exclude).sdlc"`
- (guard) `git diff main -- . ':(exclude).sdlc' ':(exclude)plugins/sdlc-lite/adapters/codex/agents' | grep '^+' | { ! grep -q '—'; }`
- No requirement in the four closed ticket handoffs is unmet or silently dropped; each gap is named with evidence.
- At least two injected defects were each caught by a selftest or check, with the defect and the failure stated.
