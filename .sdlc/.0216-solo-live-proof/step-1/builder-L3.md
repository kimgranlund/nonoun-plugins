<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `docs/reports/solo-live-run.md` (new): the validation record, with Environment, Method, a Claude Code section, a Codex section, and Limits.
- `docs/reports/solo-live-run/` (new, 21 files): `lane.txt`. `fixture/` holds the ticket handoff, `hidden_check.py`, the brief, the env wrapper, and the base hidden-check output. `claude/` and `codex/` each hold `session-trace.txt`, `verifier-L3.md`, `runs.jsonl`, `verifier-L3.attempt.json`, `skips.md`, `solo.diff`, and `hidden-check.txt`. `codex/` also holds `parent-prompt.txt`.
- `docs/README.md`: one line linking `validation/solo-live-run.md`.

## Checks
- Fixture hidden check against the pristine project: `hidden_check: 2/20 passed`, exit 1. The check bites.
- `python3 plugins/sdlc-lite/scripts/steps.py lane .sdlc/slug-max-length`, run on a pristine copy and on each arm's copy: printed `solo` with `reason: size M decides before planning (no planner result yet)` all three times.
- Dry runs of `run.sh verifier L3` from a project copy: the Claude backend chose `--model fable --effort xhigh`, and `SDLC_BACKEND=codex` chose `--model gpt-6-astra --effort high`.
- Claude arm: `claude -p --plugin-dir <plugin> --agent sdlc-lite:solo --model sonnet --effort xhigh ...`
  - Exit 0. The init model was `claude-sonnet-5-5`.
  - The solo itself ran `run.sh verifier L3`, which used `fable` `xhigh` (`claude-fable-5-1`). Verdict: pass.
  - Hidden check: 20/20, exit 0.
  - Cost: solo session 1.114 USD plus verifier 4.678 USD.
  - Wall time: 613 s for the session, which includes the verifier's 470 s.
- Codex arm: the parent `codex exec ... -c agents.enabled=true` spawned `sdlc-solo-l2`.
  - Exit 0. The subagent's rollout shows `agent_role: sdlc-solo-l2`, `gpt-6.1-sol` `high`.
  - Hidden check: 20/20, exit 0.
  - The solo ran no verifier.
- External Codex verifier: `SDLC_BACKEND=codex bash run.sh verifier L3 .sdlc/slug-max-length/handoff.md`.
  - Exit 0, `gpt-6-astra` `high`, exec transport. Verdict: pass. Took 153.6 s.
- `test -f docs/reports/solo-live-run.md`: exit 0
- `grep -q "solo-live-run.md" docs/README.md`: exit 0
- `grep -qi "claude" ... && grep -qi "codex" docs/reports/solo-live-run.md`: exit 0
- `grep -q "gpt-6.1-sol" docs/reports/solo-live-run.md`: exit 0
- `test -d docs/reports/solo-live-run`: exit 0
- `git diff --check main -- plugins docs`: exit 0. I ran it with `git add -N` on the new files so their content was actually checked, then reset the intent-to-add.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: `ok: 216 tickets, roadmap current`, exit 0
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. Its output included `skip: shellcheck not installed`.

## Notes
1. `.sdlc/0216-solo-live-proof/step-1/handoff.md` has a working-tree change I did not make: a wording edit to the steps.py line under Read first. I followed the handoff as it read when I started.
2. Run bare, `git diff --check main -- plugins docs` skips untracked files, so it would pass without looking at the new record or evidence dir. I checked them with `git add -N` (exit 0), then reset, so the index is unchanged.
3. Defect in solo.md: it says "Read nothing else unless a check failure points there", but its Verification step sends the reader to `agents/conductor.md` and asks for `## Acceptance criteria` without naming a format. As a result the Claude solo read `agents/conductor.md`, the head of `run.sh`, and part of `skills/handoff-format/SKILL.md`, and grepped the whole plugin.
4. Defect, solo.md against the generated Codex instructions: solo.md says "On Codex the verifier is `sdlc-verifier-l3`". The generated `sdlc-solo-l*` instructions say "Do not spawn further agents from an individual role" and "never start another Codex CLI from a sandboxed shell". The subagent's sandbox also had network off. A Codex solo running as a native subagent therefore has no stated way to launch its own verifier, so on Codex I launched the verifier from outside.
5. The Codex arm is confounded. My parent prompt's "do not ... spawn any other agent yourself" was meant for the parent, but the solo cited it ("the user prohibits spawning another agent"). A rerun needs a parent prompt without that line before it can show whether a Codex solo launches its own verifier.
6. On Claude, the solo added one test after the verifier passed and did not run the verifier again. The hidden check ran on the final tree.
7. The Claude solo session's cost includes 0.597 USD of `claude-fable-5-1`, from this machine's user-level `advisor` tool, not the plugin. Codex reports no USD because the login is ChatGPT, so the record gives token counts instead.
8. One em dash is in `docs/reports/solo-live-run/codex/session-trace.txt`, inside a verbatim quote of the Codex solo's report. I left the evidence unaltered. The record and the README line have none.
9. The throwaway dir `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/solo-live.WxYaOaJq96` stays on disk with the raw streams, as the record says. I created no worktrees.
10. Total Claude spend was about 5.79 USD, under the 15 USD budget.
