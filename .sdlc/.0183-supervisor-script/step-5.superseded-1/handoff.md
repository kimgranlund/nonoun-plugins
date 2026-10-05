## Task goal
A deterministic script, with no model call, that notices new mail for a harness whose host is idle and resumes that host from a headless call, inside hard limits, and can be stopped.

## Step 5: Live runs on Claude Code and Codex, recorded
level: L3
### Do
Depends on: steps 1 to 4.

Targets:
- `docs/reports/supervisor-live-run/<arm>.txt`, one per arm;
- `docs/reports/supervisor-live-run.md`;
- one line in `docs/README.md`.

1. Run `python3 docs/reports/supervisor-live-run/probe.py selftest`. If it fails, stop with Status blocked.
2. Record:
   - `claude --version`, `codex --version`, and `codex login status`;
   - `git rev-parse --short HEAD`;
   - `git status --porcelain -- plugins/ docs/`. Steps 1 to 4 are uncommitted, because builders never commit, and the record says so.
3. Run each arm once as its own foreground Bash call, with the Bash timeout at 1800000, in this order: `dry-run`, `claude`, `claude-attached`, `claude-push`, `codex`, `codex-attached`, `codex-push`. The command is `set -o pipefail; python3 docs/reports/supervisor-live-run/probe.py <arm> | tee docs/reports/supervisor-live-run/<arm>.txt`.
   - Never edit an evidence file by hand and never use a fixture.
   - Never run `supervisor.py watch --run` from this repository.
   - Never push to this repository's remote.
4. Allowed outcomes:
   - `dry-run` and all three Claude arms must pass. `claude` runs this pipeline.
   - Each Codex arm passes, or ends `result=unverified reason=host cannot run: <why>`.
   - When any arm ends `result=fail ...`, or a Claude arm ends unverified:
     - still write the record (item 5);
     - end with Status blocked, Notes starting `live proof failed: <arm>: <last line>`;
     - do not rerun the arm and do not change `supervisor.py`. A fix is a replan.
5. Write `docs/reports/supervisor-live-run.md`, modelled on `docs/reports/messages-wait-live-run.md`:
   - `# Supervisor live run`, a blank line, `Recorded: <YYYY-MM-DD>`, and an intro paragraph.
   - `## Environment`: versions, login, models from the hosts' own records, plugin commit and uncommitted state, macOS, temp location.
   - `## Method`: the exact probe and host commands, the message body and prompts verbatim, the limits used, and the oracle.
   - `## Claude Code` and `## Codex`: per arm, the evidence lines in a fenced block, what the wake log shows, the wake cost, and one line `Result <arm>: <word>`. The word is the one after `result=` on the evidence file's last line.
   - `## Negative controls`: the `dry-run` arm with its own `Result dry-run: <word>` line, plus the push arms as the mechanism probe.
   - `## Limits`: one run per arm on one machine and account; the attached idle signal cannot tell an idle open terminal from a closed one (D12); Codex MCP and connector tools are not blocked (D3); anything else the run found.
   - Write any quoted U+2014 as `\u2014`. The record holds no em dash.
6. In `docs/README.md`, add after the `Messages wait live run` line:

   `- [Supervisor live run](validation/supervisor-live-run.md): dated live run for T-0183 in which supervisor.py woke an idle Claude Code host and an idle Codex host on new mail, in ephemeral and attached mode, with a dry-run control and a push-denial probe; Claude Code <result>, Codex <result>.`
### Acceptance criteria
- `for a in dry-run claude claude-attached claude-push; do test "$(tail -n 1 docs/reports/supervisor-live-run/$a.txt)" = "result=pass" || exit 1; done`
- `for a in codex codex-attached codex-push; do tail -n 1 docs/reports/supervisor-live-run/$a.txt | grep -qE "^result=(pass|unverified reason=host cannot run: .+)$" || exit 1; done`
- `for a in dry-run claude codex claude-attached codex-attached claude-push codex-push; do head -n 1 docs/reports/supervisor-live-run/$a.txt | grep -qxF "arm=$a" || exit 1; done`
- `for a in claude codex claude-attached codex-attached; do f=docs/reports/supervisor-live-run/$a.txt; test -f "$f" || exit 1; if test "$(tail -n 1 "$f")" = "result=pass"; then python3 -c 'import re,sys; L=open(sys.argv[1]).read().splitlines(); v=dict(x.split("=",1) for x in [l for l in L if l.startswith("send_time=")][0].split(" ")[:3]); T=re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{6}Z"); s=[v["send_time"],v["read_time"],v["ack_time"]]; assert all(T.fullmatch(x) for x in s), "stamps"; assert sorted(s)==s, "order"; assert "wakes=1" in L, "wakes"; assert "reply=yes" in L, "reply"; assert "message_state=done" in L, "state"; assert "remote_commits_added=0" in L, "remote"; assert "push_attempt=denied" in L or "push_attempt=absent" in L, "push"' "$f" || exit 1; fi; done`
- `for a in claude-push codex-push; do f=docs/reports/supervisor-live-run/$a.txt; test -f "$f" || exit 1; if test "$(tail -n 1 "$f")" = "result=pass"; then grep -qxF "push_attempt=denied" "$f" || exit 1; grep -qxF "remote_commits_added=0" "$f" || exit 1; fi; done`
- `f=docs/reports/supervisor-live-run/dry-run.txt; grep -qxF "wakes=0" "$f" && grep -qxF "message_state=new" "$f"`
- `for f in docs/reports/supervisor-live-run/*.txt; do test -f "$f" || exit 1; if grep -q "^remote=" "$f"; then grep "^remote=" "$f" | grep -qE "^remote=/(private/)?(var/folders|tmp)/" || exit 1; fi; done`
- `f=docs/reports/supervisor-live-run.md; grep -qE "^Recorded: 2026-[0-9]{2}-[0-9]{2}$" "$f" && for h in "## Environment" "## Method" "## Claude Code" "## Codex" "## Negative controls" "## Limits"; do grep -qxF "$h" "$f" || exit 1; done`
- `python3 -c 'import re; t=open("docs/reports/supervisor-live-run.md").read(); ev=lambda a: open("docs/reports/supervisor-live-run/"+a+".txt").read().splitlines()[-1].split(" ")[0].split("=",1)[1]; bad=[a for a in ("dry-run","claude","codex","claude-attached","codex-attached","claude-push","codex-push") if re.findall(r"^Result "+re.escape(a)+r": (\w+)$", t, re.M)!=[ev(a)]]; assert not bad, bad'`
- `grep -F "validation/supervisor-live-run.md" docs/README.md | grep -qF "T-0183"`
- `for f in docs/reports/supervisor-live-run.md docs/reports/supervisor-live-run/*.txt docs/reports/supervisor-live-run/probe.py; do test -f "$f" || exit 1; ! grep -qF "$(printf '\342\200\224')" "$f" || exit 1; done`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/ticket-stages/watcher-design.md -e docs/reports/idle-host-watcher-design-review.md -e plugins/sdlc-lite/scripts/check.sh -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxE "plugins/sdlc-lite/scripts/supervisor\.py|docs/reports/supervisor-live-run\.md|docs/reports/supervisor-live-run/(probe\.py|AGENTS\.md|CLAUDE\.md|[a-z-]+\.txt)")"`
