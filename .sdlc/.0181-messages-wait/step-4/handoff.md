## Task goal
A parent host can wait for mail with one blocking command instead of a polling subagent, and the command never claims, moves, or prints a message body.

## Step 4: Live proof of wait on Claude Code and Codex
level: L3
### Do
Targets:
- `docs/validation/messages-wait-live-run/claude.txt`
- `docs/validation/messages-wait-live-run/codex.txt`
- `docs/validation/messages-wait-live-run.md`
- one line in `docs/README.md`

Depends on: steps 1, 2, and 3.

1. Run `python3 docs/validation/messages-wait-live-run/probe.py selftest` first. If it fails, stop with Status blocked.
2. Before the arms, record the output of:
   - `claude --version`, `codex --version`, and `codex login status`;
   - `git rev-parse --short HEAD`;
   - `git status --porcelain -- plugins/`. The step 1 and 2 changes are uncommitted, because builders never commit, and the record says so.
3. Run each arm once, as one foreground Bash call with the Bash timeout at 1200000:
   - `set -o pipefail; python3 docs/validation/messages-wait-live-run/probe.py claude | tee docs/validation/messages-wait-live-run/claude.txt`
   - the same command with `codex` and `codex.txt`.

   Never write or edit an evidence file by hand and never use a fixture. Never change the probe, the prompt, the send delay, or the oracle after an arm has run.
4. Allowed outcomes per arm:
   - The Claude arm must pass. The `claude` CLI is the one that runs this pipeline, and it printed `2.1.286 (Claude Code)` at plan time.
   - The Codex arm must pass, or end with a last line that starts with `result=unverified reason=host cannot run: `. That is the handoff's one fallback: "If a host cannot run, record the arm as unverified with the reason".
5. When an arm's last line is `result=fail ...`, the live proof did not hold.
   - Keep the evidence file and still write the record (item 6) with `Result: fail` for that arm.
   - End with Status blocked. The first line of Notes is `live proof failed: <arm>: <the result line>`.
   - Do not rerun the arm. Whether to rerun, change the prompt, or accept the finding is the user's decision at the replan: /chain 4.2 routes a blocked builder to a planner L3 replan.
6. Write `docs/validation/messages-wait-live-run.md`, modelled on `docs/validation/messages-live-run.md`:
   - `# Messages wait live run`, a blank line, `Recorded: <YYYY-MM-DD>` with the run date, and an intro paragraph on what was shown.
   - `## Environment`:
     - the version and login output from item 2;
     - the models from each host's own records: the Claude init event's `model` in `host-stdout.jsonl`, and the Codex rollout's `turn_context` model and effort;
     - the plugin commit, and whether `plugins/` held uncommitted step 1 and 2 changes;
     - that the probe dropped `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS`;
     - macOS and the temp project location.
   - `## Method`:
     - the exact probe and host commands, and the prompt verbatim;
     - the 20-second send delay;
     - the definitions of `wait_calls`, `poll_calls`, `wait_returned`, and `wait_before_send`;
     - the oracle, the exit codes, and the isolation proof per host, as in the T-0179 record.
   - `## Claude Code` and `## Codex`, one section per arm:
     - a link to the arm's evidence file and its lines quoted in a fenced block;
     - what the raw stream shows: the wait call, its returned line, and the read, reply, and ack calls;
     - for Codex, also what the rollout shows: the `exec` input with its `yield_time_ms`, and any `write_stdin` or cell `wait`;
     - exactly one line `Result: <pass|fail|unverified>`, equal to the word after `result=` on the evidence file's last line.
   - `## Limits`:
     - one run per arm, on one machine and one account per host;
     - an active parent only, and no idle-host wake (T-0182);
     - `poll_calls` counts only the listed call kinds, and other shell calls appear as `tool=` lines;
     - any probe limit found.
   - Where a quoted evidence line holds U+2014, write `\u2014` in its place and say so under Limits. The record holds no em dash.
7. In `docs/README.md`, add one line right after the `- [Messages live run](validation/messages-live-run.md): ...` line (line 33). Fill in each arm's result word:
   ```text
   - [Messages wait live run](validation/messages-wait-live-run.md): dated live run for T-0181 in which a fresh Claude Code host and a fresh Codex host were each told to make one `messages.py wait` call, then read, reply, and ack; Claude Code <result>, Codex <result>.
   ```
### Acceptance criteria
- `test "$(tail -n 1 docs/validation/messages-wait-live-run/claude.txt)" = "result=pass"`
- `tail -n 1 docs/validation/messages-wait-live-run/codex.txt | grep -qE "^result=(pass|unverified reason=host cannot run: .+)$"`
- `for a in claude codex; do head -n 1 docs/validation/messages-wait-live-run/$a.txt | grep -qxF "arm=$a" || exit 1; done`
- `for f in docs/validation/messages-wait-live-run/claude.txt docs/validation/messages-wait-live-run/codex.txt; do test -f "$f" || exit 1; if test "$(tail -n 1 "$f")" = "result=pass"; then python3 -c 'import re,sys; L=open(sys.argv[1]).read().splitlines(); mid=[l for l in L if l.startswith("message=")][0].rsplit("/",1)[1][:-3]; v=dict(x.split("=",1) for x in [l for l in L if l.startswith("send_time=")][0].split(" ")[:3]); T=re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{6}Z"); s=[v["send_time"],v["read_time"],v["ack_time"]]; assert "wait_calls=1 poll_calls=0" in L, "calls"; assert "wait_before_send=yes" in L, "before"; assert "wait_returned="+mid in L, "returned"; assert all(T.fullmatch(x) for x in s), "stamps"; assert sorted(s)==s, "order"' "$f" || exit 1; fi; done`
- `f=docs/validation/messages-wait-live-run.md; grep -qE "^Recorded: 2026-[0-9]{2}-[0-9]{2}$" "$f" && for h in "## Environment" "## Method" "## Claude Code" "## Codex" "## Limits"; do grep -qxF "$h" "$f" || exit 1; done`
- `python3 -c 'import re; t=open("docs/validation/messages-wait-live-run.md").read(); sec=lambda h: t.split("\n"+h+"\n",1)[1].split("\n## ",1)[0]; ev=lambda a: open("docs/validation/messages-wait-live-run/"+a+".txt").read().splitlines()[-1].split(" ")[0].split("=",1)[1]; got=[(re.findall(r"^Result: (\w+)$", sec(h), re.M), ev(a)) for h,a in (("## Claude Code","claude"),("## Codex","codex"))]; assert all(r==[e] for r,e in got), got'`
- `grep -qF "validation/messages-wait-live-run.md" docs/README.md`
- `for f in docs/validation/messages-wait-live-run.md docs/validation/messages-wait-live-run/probe.py; do test -f "$f" || exit 1; ! grep -qF "$(printf '\342\200\224')" "$f" || exit 1; done`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^docs/validation/messages-wait-live-run(\.md|/)")"`
