## Task goal
`plugins/sdlc-lite/scripts/messages.py` runs a git-ignored `.sdlc/messages/` mailbox with a validated schema, an explicit new, read, done lifecycle, and a tested transition table, and `run.sh` prints a count notice before it launches a role.

## Step 3: run.sh notice, run-selftest case, check.sh wiring
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1 (`messages.py count`) and step 2 (`messages.py selftest`). Edit only `run.sh`, `run-selftest.sh`, and `check.sh` in this worktree. Never edit the main checkout's `run.sh`, because role runs use it.

`plugins/sdlc-lite/scripts/run.sh`:
- Insert this block inside the `{ ... }` group (the self-edit rule, `run.sh:83-88`), after the Codex resolve and immediately before the `# Shared lifecycle owner holds the directory lock` comment (`run.sh:228`):

```
# Mailbox notice (see the header): new messages for the role and the backend; parent process only.
if [[ "${SDLC_LIFECYCLE_CHILD:-}" != 1 ]]; then
  msg_total=0
  for msg_name in "$role" "$backend"; do
    if msg_n=$(python3 "$plugin_root/scripts/messages.py" count --receiver "$msg_name" 2>/dev/null) && [[ "$msg_n" =~ ^[0-9]+$ ]]; then
      msg_total=$((msg_total + msg_n))
    fi
  done
  if (( msg_total > 0 )); then
    echo "run.sh: $msg_total new message(s) for $role; read with messages.py" >&2
  fi
fi
```

- The `SDLC_LIFECYCLE_CHILD` guard is required. `run_lifecycle.py` reruns run.sh with `SDLC_LIFECYCLE_CHILD=1`, and the child inherits its stderr (`run.sh:229-231`, `run_lifecycle.py:94-106`). Without the guard, a real run prints the notice twice. A dry run never reaches the exec, so it prints the notice too.
- The block uses if-statements, so `set -e` cannot abort on a failed count. A failed or non-numeric count adds 0, and a missing mailbox counts `0`. The block never prints a body and never changes an exit code.
- Add a header paragraph: "Mailbox notice: before launching a role (dry runs too, never in the run_lifecycle.py child), run.sh adds messages.py count --receiver for the role name and for the backend name (claude or codex). When the sum is above 0 it prints one stderr line "run.sh: <n> new message(s) for <role>; read with messages.py". A failed count adds 0. It never prints a body and never changes the exit code."

`plugins/sdlc-lite/scripts/run-selftest.sh`: add a notice case before the final `echo "run selftest: PASS"`, with a matching header sentence. The case uses a new throwaway repo (git init plus a commit, as the other cases do) holding `h.md`:
- (a) A planner dry run with no mailbox exits 0, prints nothing on stderr, and creates no `.sdlc`.
- (b) After `python3 "$here/messages.py" send --receiver planner ...`, a planner dry run's stderr is exactly `run.sh: 1 new message(s) for planner; read with messages.py`.
- (c) After one more message, to receiver `claude`, a planner dry run's stderr is exactly the same line with 2. A builder dry run's stderr is exactly `run.sh: 1 new message(s) for builder; read with messages.py`.
- (d) A real planner run through the stub `$tmp/bin/claude` exits 0 and prints the notice line exactly once. Its stdout and stderr hold no message body.
- Each failure reads `fail "notice: <reason>"`.
- The existing exact-stderr dry runs (`nvmrc_err`, `run-selftest.sh:203-231`) use repos without a mailbox, so they stay unchanged.

`plugins/sdlc-lite/scripts/check.sh`: add `python3 "$root/scripts/messages.py" selftest || fail=1` after the traces line, and name messages.py in the header's selftest list.

Contract dependents:
- `run-selftest.sh` is handled above.
- `run_lifecycle.py` stays untouched, because the guard keeps the child silent.
- `lifecycle-selftest.py` and `codex-selftest.py` stay untouched. They run run.sh in temp repos with no mailbox, and check stderr only with `assertIn` (`lifecycle-selftest.py:52-58`, `codex-selftest.py:80`).
- `check.py` does not read `check.sh`.

The criteria below fail today at the missing `messages.py`. Once steps 1 and 2 are built, they fail on the missing notice. A plugin copy with a stub `messages.py` showed this:
- With no notice, all three run.sh criteria failed.
- With the guarded block, they passed, and so did `run-selftest.sh`.
- With the block but no guard, the real-run criterion failed with two notice lines.
### Acceptance criteria
- `d=$(mktemp -d) && S="$PWD/plugins/sdlc-lite/scripts" && git -C "$d" init -q && git -C "$d" -c user.email=a@b -c user.name=a -c commit.gpgsign=false commit -q --allow-empty -m init && ( cd "$d" && printf "x\n" > h.md && SDLC_DRY_RUN=1 bash "$S/run.sh" planner L2 h.md >/dev/null 2>e0 && test ! -s e0 && test ! -e .sdlc && python3 "$S/messages.py" send --receiver planner --sender alice --topic t --follow-up false hi >/dev/null && SDLC_DRY_RUN=1 bash "$S/run.sh" planner L2 h.md >/dev/null 2>e1 && test "$(cat e1)" = "run.sh: 1 new message(s) for planner; read with messages.py" )`
- `d=$(mktemp -d) && S="$PWD/plugins/sdlc-lite/scripts" && git -C "$d" init -q && git -C "$d" -c user.email=a@b -c user.name=a -c commit.gpgsign=false commit -q --allow-empty -m init && ( cd "$d" && printf "x\n" > h.md && python3 "$S/messages.py" send --receiver claude --sender codex --topic t --follow-up false secret-body-77 >/dev/null && python3 "$S/messages.py" send --receiver planner --sender alice --topic t --follow-up false secret-body-78 >/dev/null && python3 "$S/messages.py" send --receiver builder --sender alice --topic t --follow-up false secret-body-79 >/dev/null && SDLC_DRY_RUN=1 bash "$S/run.sh" planner L2 h.md >o 2>e && test "$(cat e)" = "run.sh: 2 new message(s) for planner; read with messages.py" && ! grep -qF secret-body o && ! grep -qF secret-body e )`
- `d=$(mktemp -d) && S="$PWD/plugins/sdlc-lite/scripts" && mkdir "$d/bin" "$d/r" && jq -nc '{type:"result",is_error:false,result:"## Goal\nok",total_cost_usd:0,duration_ms:1,num_turns:1}' > "$d/res.json" && printf "%s\n" "#!/bin/sh" "cat \"$d/res.json\"" > "$d/bin/claude" && chmod +x "$d/bin/claude" && git -C "$d/r" init -q && git -C "$d/r" -c user.email=a@b -c user.name=a -c commit.gpgsign=false commit -q --allow-empty -m init && ( cd "$d/r" && printf "x\n" > h.md && python3 "$S/messages.py" send --receiver planner --sender alice --topic t --follow-up false secret-body-80 >/dev/null && PATH="$d/bin:$PATH" bash "$S/run.sh" planner L2 h.md >o 2>e && test "$(grep -c "new message(s)" e)" = 1 && grep -qxF "run.sh: 1 new message(s) for planner; read with messages.py" e && ! grep -qF secret-body o && ! grep -qF secret-body e && grep -qx "ok" planner-L2.md )`
- `grep -qF "new message(s) for" plugins/sdlc-lite/scripts/run-selftest.sh && bash plugins/sdlc-lite/scripts/run-selftest.sh`
- `grep -qF "scripts/messages.py\" selftest" plugins/sdlc-lite/scripts/check.sh`
- `awk '/^\{$/ && !o {o = NR} /new message\(s\)/ {n = NR} /^\}$/ {c = NR} END {exit !(o && n > o && c > n)}' plugins/sdlc-lite/scripts/run.sh`
- (guard) `! git diff "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh plugins/sdlc-lite/scripts/check.sh | grep "^+" | grep -q "$(printf "\xe2\x80\x94")"`
- (guard) `out=$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.sh ); test -z "$out"`
