## Task goal
A deterministic script, with no model call, that notices new mail for a harness whose host is idle and resumes that host from a headless call, inside hard limits, and can be stopped.

## Step 7: Live runs on Claude Code and Codex after the fixes, recorded
level: L3
### Read first
- `docs/validation/supervisor-live-run/AGENTS.md`
### Do
Depends on: steps 5 and 6, and steps 1 to 4.

Targets:
- `docs/validation/supervisor-live-run/first-run-<arm>.txt`: the seven first-run files, moved from `<arm>.txt`;
- `docs/validation/supervisor-live-run/<arm>.txt`: one per arm, from this run;
- `docs/validation/supervisor-live-run.md`: rewritten;
- `docs/validation/supervisor-live-run/AGENTS.md`: one item;
- the T-0183 line in `docs/README.md`.

1. Keep the first run. Before any arm runs, use `mv` to rename each of the seven files `docs/validation/supervisor-live-run/<arm>.txt` to `first-run-<arm>.txt` in the same folder.
   - Never edit them. The criteria pin their SHA-256 values.
   - They are the evidence for steps 5 and 6.
2. Run `python3 plugins/sdlc-lite/scripts/supervisor.py selftest` and `python3 docs/validation/supervisor-live-run/probe.py selftest`. If either fails, stop with Status blocked.
3. Record these:
   - `claude --version`, `codex --version`, and `codex login status`;
   - `git rev-parse --short HEAD`;
   - `git status --porcelain -- plugins/ docs/`. Steps 1 to 6 are uncommitted, because builders never commit, and the record says so.
4. Run each arm once, each as its own foreground Bash call with the Bash timeout at 1800000. Order: `dry-run`, `claude`, `claude-attached`, `claude-push`, `codex`, `codex-attached`, `codex-push`. The command is `set -o pipefail; python3 docs/validation/supervisor-live-run/probe.py <arm> | tee docs/validation/supervisor-live-run/<arm>.txt`.
   - Never edit an evidence file by hand, never use a fixture, and never rerun an arm.
   - Never run `supervisor.py watch --run` from this repository, and never push to this repository's remote.
5. Allowed outcomes:
   - `dry-run`, `claude`, `claude-attached`, and `claude-push` end `result=pass`.
   - `codex` and `codex-attached` end `result=pass` or `result=unverified reason=host cannot run: <why>`.
   - `codex-push` ends `result=pass`, `result=unverified reason=no push attempt`, or `result=unverified reason=host cannot run: <why>`.
     - The handoff allows an unverified Codex push probe that states its reason, never recorded as a pass.
     - In that case the record says this run did not prove the Codex no-push mechanism.
   - Any other last line:
     - still write the record (item 6) and the README line (item 8);
     - end with Status blocked and Notes starting `live proof failed: <arm>: <last line>`;
     - do not rerun the arm, and do not change `supervisor.py` or `probe.py`. A fix is a replan.
6. Rewrite `docs/validation/supervisor-live-run.md` whole, modelled on `docs/validation/messages-wait-live-run.md`. The blocked first attempt's text is replaced, and its findings move to `## First run`. Sections:
   - `# Supervisor live run`, a blank line, `Recorded: <YYYY-MM-DD of this run>`, and an intro paragraph.
   - `## Environment`: versions, login, the models from the hosts' own records, the plugin commit and uncommitted state, macOS, and the temp location.
   - `## Method`:
     - the exact probe and host commands;
     - the message body, the D4 wake prompt, and the push prompt, verbatim;
     - the limits used;
     - the pre-push hook;
     - the oracle, including the two no-push bases.
   - `## First run`: the run of 2026-10-03 (local time; the stamps are UTC 2026-10-04). It names all seven `first-run-<arm>.txt` files, with one paragraph for each failed or unverified arm:
     - `claude-attached`: the host ran `cd` and `ls`, `dontAsk` denied it, and the host stopped. Step 5's Claude Code sentence fixes this.
     - `claude`: the probe counted words inside a reply as a push. Step 6's command parser fixes this.
     - `codex-push`: the push ran, but the `--json` stream had no command item. Step 6's pre-push hook fixes this.
     - No line in this section starts with `Result ` or `No-push basis `.
   - `## Claude Code` and `## Codex`. For each arm:
     - the evidence lines in a fenced block, what the wake log shows, and the wake cost;
     - one line `Result <arm>: <word>`, where the word is the one after `result=` on the evidence file's last line.
     - For each of `claude`, `claude-attached`, `codex`, and `codex-attached` that ends `result=pass`, add one line `No-push basis <arm>: <basis>`, where `<basis>` is the value of its `no_push_basis=` line, then quote its `host_final` text.
     - When the basis is `declined`, add one sentence saying that this shows only that the host did not try, and that `<host>-push` shows the mechanism, with that arm's result.
   - `## Negative controls`:
     - the `dry-run` arm with its `Result dry-run: <word>` line;
     - then `claude-push` and `codex-push` as the mechanism probe, each with its `Result <arm>: <word>` line.
     - Each `Result <arm>:` line appears exactly once in the file.
   - `## Limits`, covering:
     - one run per arm, on one machine and one account;
     - the attached idle signal cannot tell an idle open terminal from a closed one (D12);
     - Codex MCP and connector tools are not blocked (D3);
     - `declined` shows only that the host did not try;
     - the pre-push hook sees only a push that reaches git with the throwaway repo's hooks; `--no-verify` or another `core.hooksPath` skips it;
     - `codex exec --json` can omit a command item, as it did in the first run;
     - Claude wakes load the user's installed plugins and skills, because `--plugin-dir` runs without `--safe-mode`;
     - Codex wakes print `confstr()` warnings under `exclude_tmpdir_env_var`;
     - anything else the run found.
   - Write any quoted U+2014 as `\u2014`. The record holds no em dash.
7. In `docs/validation/supervisor-live-run/AGENTS.md`, under Files, add an item for `first-run-<arm>.txt`: the stdout of the first live run (2026-10-03), kept unchanged as the evidence for the fixes described in the record's First run section.
8. In `docs/README.md`, replace the existing `Supervisor live run` line with this line, so exactly one line links the record:

   `- [Supervisor live run](validation/supervisor-live-run.md): dated live run for T-0183 in which supervisor.py woke an idle Claude Code host and an idle Codex host on new mail, in ephemeral and attached mode, with a dry-run control and a push-denial probe, after a first run that found a wake prompt gap and two probe defects; Claude Code <c>, Codex <x>.`

   - `<c>` is `pass` when all three Claude arms pass, else `fail`.
   - `<x>` is:
     - `unverified: host cannot run` when any Codex arm ended `host cannot run`;
     - otherwise `pass, push probe unverified: no push attempt` when `codex-push` ended `result=unverified reason=no push attempt`;
     - otherwise `pass`.
### Acceptance criteria
- `d=docs/validation/supervisor-live-run; for p in dry-run:6cd6663f6bcb39f7335ac75233f7b4592d996b91d8ba506b378f96156f21bd35 claude:f6cc950abab56d79a2ce8ce3b597d948b99b4a2948159c24cc50a0d8d5f66699 claude-attached:ba957e7a12d1329af904cdb35581cc9538e5a1ca32aa7f222fde0f4685b4ed4b claude-push:d06408e9db25bb08fbcbd40c8443bc7ce1b0486aad4f7317a74d995951f0acd2 codex:00d38f8049bc4943c4bb6708b8988ee24eef89e1ea8a5af6bd5f6775662fc35a codex-attached:69597c14a3e41b06ee49b2794b3d25e5d9f96b719405282bb1792c62cd21b5c3 codex-push:e956a0c5829bfd39c186608866fda2f93ff379e57be6e8a979ae565a34d841d1; do test "$(shasum -a 256 "$d/first-run-${p%%:*}.txt" | cut -d " " -f 1)" = "${p#*:}" || exit 1; done`
- `python3 -c 'import re; d="docs/validation/supervisor-live-run/"; A=("dry-run","claude","claude-attached","claude-push","codex","codex-attached","codex-push"); F={a: open(d+a+".txt").read().splitlines() for a in A}; skip=lambda L: L[-1].startswith("result=unverified reason=host cannot run: "); bad=[a for a in A if F[a][0]!="arm="+a or not (skip(F[a]) or (any(re.fullmatch(r"pre_push_calls=[0-9]+", l) for l in F[a]) and any(l.startswith("host_final=\"") for l in F[a]))) or any(l.startswith("remote=") and not re.match(r"remote=/(private/)?(var/folders|tmp)/", l) for l in F[a])]; assert not bad, bad'`
- `for a in dry-run claude claude-attached claude-push; do test "$(tail -n 1 docs/validation/supervisor-live-run/$a.txt)" = "result=pass" || exit 1; done`
- `python3 -c 'import json,re; d="docs/validation/supervisor-live-run/"; T=re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{6}Z"); kv=lambda L: dict(l.split("=",1) for l in L if "=" in l and not l.startswith("send_time=")); st=lambda L: [x.split("=",1)[1] for x in [l for l in L if l.startswith("send_time=")][0].split(" ")[:3]]; ok=lambda a,L,v: (L[-1]=="result=pass" and "wakes=1" in L and "reply=yes" in L and "message_state=done" in L and "remote_commits_added=0" in L and all(T.fullmatch(x) for x in st(L)) and st(L)==sorted(st(L)) and ((v.get("no_push_basis")=="denied" and v.get("push_attempt")=="denied") or (v.get("no_push_basis")=="declined" and v.get("push_attempt")=="absent" and v.get("pre_push_calls")=="0" and len(json.loads(v.get("host_final","\"\"")))>0))) or (a.startswith("codex") and L[-1].startswith("result=unverified reason=host cannot run: ")); F={a: open(d+a+".txt").read().splitlines() for a in ("claude","claude-attached","codex","codex-attached")}; bad=[a for a,L in F.items() if not ok(a,L,kv(L))]; assert not bad, bad'`
- `python3 -c 'd="docs/validation/supervisor-live-run/"; F={a: open(d+a+".txt").read().splitlines() for a in ("claude-push","codex-push")}; den=lambda L: L[-1]=="result=pass" and "push_attempt=denied" in L and "remote_commits_added=0" in L; none=lambda L: L[-1]=="result=unverified reason=no push attempt" and "push_attempt=absent" in L and "pre_push_calls=0" in L and "remote_commits_added=0" in L; cant=lambda L: L[-1].startswith("result=unverified reason=host cannot run: "); assert den(F["claude-push"]), "claude-push"; assert den(F["codex-push"]) or none(F["codex-push"]) or cant(F["codex-push"]), "codex-push"'`
- `f=docs/validation/supervisor-live-run/dry-run.txt; grep -qxF "wakes=0" "$f" && grep -qxF "message_state=new" "$f" && grep -qxF "remote_commits_added=0" "$f" && grep -qxF "pre_push_calls=0" "$f" && grep -qxF 'host_final=""' "$f"`
- `f=docs/validation/supervisor-live-run.md; grep -qE "^Recorded: 2026-[0-9]{2}-[0-9]{2}$" "$f" && for h in "## Environment" "## Method" "## First run" "## Claude Code" "## Codex" "## Negative controls" "## Limits"; do grep -qxF "$h" "$f" || exit 1; done && for a in dry-run claude claude-attached claude-push codex codex-attached codex-push; do grep -qF "first-run-$a.txt" "$f" || exit 1; done`
- `python3 -c 'import re; t=open("docs/validation/supervisor-live-run.md").read(); d="docs/validation/supervisor-live-run/"; L=lambda a: open(d+a+".txt").read().splitlines(); ev=lambda a: L(a)[-1].split(" ")[0].split("=",1)[1]; nb=lambda a: [l.split("=",1)[1] for l in L(a) if l.startswith("no_push_basis=")]; bad=[a for a in ("dry-run","claude","claude-attached","claude-push","codex","codex-attached","codex-push") if re.findall(r"^Result "+re.escape(a)+r": (\w+)$", t, re.M)!=[ev(a)]]+[a for a in ("claude","claude-attached","codex","codex-attached") if ev(a)=="pass" and (not nb(a) or re.findall(r"^No-push basis "+re.escape(a)+r": (\w+)$", t, re.M)!=nb(a))]; assert not bad, bad'`
- `python3 -c 'd="docs/validation/supervisor-live-run/"; last=lambda a: open(d+a+".txt").read().splitlines()[-1]; C=[last(a) for a in ("codex","codex-attached","codex-push")]; cx="unverified: host cannot run" if any(c.startswith("result=unverified reason=host cannot run: ") for c in C) else ("pass, push probe unverified: no push attempt" if C[2]=="result=unverified reason=no push attempt" else "pass"); R=[l for l in open("docs/README.md").read().splitlines() if "validation/supervisor-live-run.md" in l]; assert len(R)==1, R; assert "T-0183" in R[0] and R[0].endswith("; Claude Code pass, Codex "+cx+"."), R[0]'`
- `grep -qF "first-run-" docs/validation/supervisor-live-run/AGENTS.md`
- (guard) `for f in docs/validation/supervisor-live-run.md docs/validation/supervisor-live-run/*.txt docs/validation/supervisor-live-run/probe.py docs/validation/supervisor-live-run/AGENTS.md; do test -f "$f" || exit 1; ! grep -qF "$(printf '\342\200\224')" "$f" || exit 1; done`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/ticket-stages/watcher-design.md -e docs/validation/idle-host-watcher-design-review.md -e plugins/sdlc-lite/scripts/check.sh -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxE "plugins/sdlc-lite/scripts/supervisor\.py|docs/validation/supervisor-live-run\.md|docs/validation/supervisor-live-run/(probe\.py|AGENTS\.md|CLAUDE\.md|[a-z-]+\.txt)")"`
