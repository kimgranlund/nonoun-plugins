<!-- role=solo level=L2 model=opus effort=medium -->
## Output
🟢 T-0532 is built and the independent verifier passed it; nothing is committed, as briefed.

**Files changed**
- `plugins/sdlc-lite/scripts/steps.py`: `split --supersede` renames a chosen step dir that holds role output to the next free `step-<n>.superseded-<k>` after every check passes, then splits. `swap` accepts a solo task folder, using the newest `solo-L<n>.md` in place of the builder result and reading the ticket's `## Acceptance criteria`. Usage text and selftest cases added.
- `plugins/sdlc-lite/agents/verifier.md`: rule 5 now says to shard a suite that cannot finish within the 600000 ms foreground cap.
- Regenerated, not hand-edited: `agents/verifier-L1|L2|L3.md` and the six `adapters/codex/agents/sdlc-verifier-l*.toml`.
- `.sdlc/0532-step-tooling-long-suites/handoff.md`: `## Acceptance criteria` added. Run records sit beside it.

**Checks**
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exit 0
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -c 'supersede\|solo task dir'` exit 0 (prints 17)
- `grep -n shard plugins/sdlc-lite/agents/verifier.md` exit 0 (line 22)
- `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check && python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0
- `bash plugins/sdlc-lite/scripts/check.sh` exit 0 (about 37 minutes)

**New selftest cases**
- `split --supersede` on `step-2` with `builder-L2.md` moves it to `step-2.superseded-1` and writes a new `step-2`; a second run takes `superseded-2`.
- Without the flag it refuses and writes nothing, and with the flag nothing is renamed when another check refuses.
- `swap` on a solo dir with `solo-L2.md` and a plan-defect verifier fail applies the swap; a dir with neither a builder nor a solo result refuses.

**Verifier**
L2 (Sonnet high): pass on all five criteria, no out-of-scope changes. It broke each new code path on a copy and saw the matching selftest cases fail. `dispatch.py record` ran (rc 0) and left the run unpriced, because no transcript was passed.

**Still open**
- 🟡 `skills/chain/SKILL.md` section 4.2 still describes only the manual rename. It stays correct, but does not mention `--supersede`; that file is outside this ticket's scope, so it is a follow-up ticket.
- 🟡 Cosmetic: the swap usage text at `steps.py:355-358` has one overlong line.
- 🟡 My own red-before evidence for the two new paths is by reasoning only; the verifier's break-it runs are the observed negative controls.

verify: needed (done: verifier-L2 pass, `.sdlc/0532-step-tooling-long-suites/verifier-L2.md`)
