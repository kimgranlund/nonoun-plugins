<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
fail

## Criteria
- `test "$(grep -l 'cannot wake an idle host' <5 files> | wc -l)" -eq 5`: pass. Evidence: ran the command and it exited 0 (c1=0). The phrase is in `messages.py` at line 251 (docstring), the messenger.md body, design.md, codex-role-execution.md and the new note. The `messages.py` hit is in the module docstring, not in `ENTRY_TEMPLATE`. Line 245 shows the `## Host limits` heading inside the docstring (lines 2-158), and `ENTRY_TEMPLATE` is at 202-256, so this edit sits at 248-251 inside the template. The builder's "template" claim holds.
- `grep -q 'messages-idle-host-limit-2026-10-01.md' docs/README.md`: pass. Evidence: exit 0, and the diff shows the one-line link next to its neighbors.
- (guard) `codex_roles.py generate --check`: pass. Evidence: "Codex agent definitions verified", exit 0. The TOML diff matches the messenger.md edit, so it was regenerated.
- (guard) `messages.py selftest`: pass. Evidence: "messages selftest: PASS".
- (guard) scope diff: pass. Evidence: exit 0. Only the allowed files changed, and `git status` shows no other non-`.sdlc` changes.
- (guard) `check.sh`: pass. Evidence: exit 0 (check=0), ending "ok: plugin validate". shellcheck is not installed and was skipped.

The two criteria hold, but the new note carries a false evidence pointer (see next section). No em dashes appear in the diff or the note (grep count 0). The four guards were not re-run at the pre-build SHA. They are green on the built tree, so there was nothing to attribute to an inherited red.

## Out of scope changes
None. The `sdlc-messenger-l1.toml` change is the required regeneration.

## For the next attempt
The note `docs/reports/messages-idle-host-limit-2026-10-01.md`, in its "Evidence it was not tested" section, cites `spawn_agent` and `wait_agent` tool calls with "raw evidence in `messages-live-run/codex-messenger.txt`". That claim is false.
- `grep -c 'wait_agent' docs/reports/messages-live-run/codex-messenger.txt` gives 0.
- `grep -c 'spawn_agent' docs/reports/messages-live-run/codex-messenger.txt` gives 0.
- The only source is `docs/reports/messages-live-run.md` line 156, which quotes the rollout files for the Codex parent: `spawn_agent`, `wait_agent`, `followup_task`, `wait_agent`.

Fix: point the evidence cite at `messages-live-run.md` (the "rollout files" section near line 156) and drop or correct the `codex-messenger.txt` reference. This was checked against the live-run record, not the builder's wording. The builder might rebut that "raw evidence" meant the live-run bundle in general. The rebuttal fails because the sentence names one file and that file has no such calls. Nothing else needs changing.
