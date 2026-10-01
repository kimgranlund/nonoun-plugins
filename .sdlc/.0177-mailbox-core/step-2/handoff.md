## Task goal
`plugins/sdlc-lite/scripts/messages.py` runs a git-ignored `.sdlc/messages/` mailbox with a validated schema, an explicit new, read, done lifecycle, and a tested transition table, and `run.sh` prints a count notice before it launches a role.

## Step 2: messages.py selftest with the race negative control
level: L4
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add the `selftest` subcommand and two test-only hooks to `plugins/sdlc-lite/scripts/messages.py`. Depends on: step 1. If a case exposes a defect in step 1's CLI, fix the CLI to step 1's interface. Never change the interface to make a case pass.

Test-only hooks in `read`'s claim. The docstring names both as selftest only:
- `SDLC_MESSAGES_TEST_CLAIM=copy-delete` swaps the rename claim for a non-atomic one: check that the source exists, copy it to the destination, wait at the barrier, then delete the source, ignoring FileNotFoundError. Any other value, or none, keeps the rename.
- `SDLC_MESSAGES_TEST_BARRIER=<dir>` makes each claimant create `<dir>/<pid>` and poll every 10 ms, for up to 10 s, until two entries exist. On a timeout it exits 1 with `barrier timeout`. In rename mode it waits just before `os.rename`; in copy-delete mode it waits between the copy and the delete.

Selftest harness:
- It runs the CLI under test as `sys.executable` plus this file's own path, so a copied and mutated file tests itself.
- Every call runs with `cwd` set to a temp git repo. Make each repo with `git init` and an empty commit under `-c user.name`, `-c user.email`, and `-c commit.gpgsign=false`, as `run-selftest.sh:91` does.
- The env drops every `SDLC_MESSAGES_TEST_*` variable, except in the race cases. The selftest never touches the caller's repo or mailbox.
- Stamp timing: before each transition, the field it stamps is empty or absent. Take t0 just before the subprocess and t1 just after, both in the stamp format, and assert t0 <= stamp <= t1. Wherever the fields are present, assert `send_time <= read_time <= ack_time`, and assert that the file exists in exactly one state folder.
- Each negative control asserts the exit code (1, or 2 for an unknown flag). It also asserts that every file under the mailbox except `.lock` is byte-identical before and after.
- It prints one `ok: <label>` line per case, in the order below and with exactly these labels, then `messages selftest: PASS`, and exits 0. On the first failure it prints `messages selftest: FAIL: <label>: <reason>` and exits 1.
- It finishes in under 60 s on this host.

Cases:
1. `create`: `send` puts the file only in `new/<r>/`, with `send_time` in its window, an empty `read_time`, the exact `protocol`, and no `ack_time`.
2. `new to read`: `read` moves the file only to `read/`, stamps `read_time` in its window, and prints the body between the markers.
3. `read to done, follow-up false`: `ack` moves the file only to `done/` and stamps `ack_time` in its window plus the `outcome`.
4. `read to done, follow-up true after a reply`: `ack` is refused before the reply and succeeds after `reply`.
5. `new to done, expired`: `expire --now` past `expires` moves an unread message to `done/` with `outcome: expired`, an empty `read_time`, and no `ack_time`.
6. `read to done, expired, no reply, notice sent`:
   - A read, unreplied follow-up message gets `outcome: expired, no reply`.
   - A notice appears in `new/<original sender>/` with `kind: ack`, `re` = the id, the same topic, body `expired, no reply`, and `follow_up_requested: false`.
   - With a reply present, the same case gets `outcome: expired` and sends no notice.
7. `refused: ack of an unread message`.
8. `refused: read by a non-recipient`.
9. `refused: backward moves`: `read` on a message in `read/` and on one in `done/`, and `ack` on one in `done/`.
10. `refused: ack with follow-up and no reply`.
11. `refused: caller-set stamps`:
    - `send` with each of `--send-time`, `--read-time`, `--ack-time`, and `--protocol` exits 2 and writes nothing.
    - A body that opens with a front matter block setting `read_time`, `ack_time`, and `protocol` is stored with an empty `read_time`, no `ack_time`, and the correct `protocol`. After `read` and `ack`, each stamp falls in its transition's window.
    - A topic or an outcome that holds a newline is refused.
12. `refused: missing required fields`:
    - `send` without each of `--receiver`, `--sender`, `--topic`, and `--follow-up` exits 1 and writes nothing.
    - For each of the seven required keys, `read` refuses a hand-written file in `new/<r>/` that lacks that key, and the file stays in place.
13. `refused: malformed file in every subcommand`: with an invalid file in place, `read`, `ack`, `reply`, `expire`, `list`, and `count` each exit 1 with empty stdout and move nothing.
14. `refused: size cap`:
    - `send` and `reply` refuse a 4001-byte body, and `read` refuses a hand-written file with one.
    - A 4000-byte body is accepted.
    - A body that holds a marker line is refused.
15. `refused: invalid names and ids`:
    - the names `Bob`, `../x`, `a/b`, and a 41-character name;
    - the ids `../x` and `a/b`;
    - a `read` path outside `new/<r>/`;
    - `--re ../x`.
16. `race: one winner`: one harness function starts two `read` subprocesses on one message with `SDLC_MESSAGES_TEST_BARRIER` set, and returns a verdict.
    - Exactly one subprocess exits 0. The other exits 1 with `already claimed` on stderr.
    - Afterwards the message is only in `read/`, with one non-empty `read_time`, and nothing is in `new/` or `done/`.
17. `race: non-atomic claim detected`: the same function with `SDLC_MESSAGES_TEST_CLAIM=copy-delete` must return a failing verdict (two winners). The selftest asserts that it does, which proves the race check bites.
18. `worktree: one shared mailbox`: a subprocess makes a detached linked worktree of the temp repo, inside the temp dir.
    - A `send` from the linked worktree, with no `--root`, lands under the main checkout's `.sdlc/messages/new/`.
    - `count` agrees from both trees.
    - No `.sdlc` exists in the linked worktree.

Write no em dash in the file.
### Acceptance criteria
- `out=$(python3 plugins/sdlc-lite/scripts/messages.py selftest) && test "$(printf "%s\n" "$out" | tail -n 1)" = "messages selftest: PASS" && for l in "create" "new to read" "read to done, follow-up false" "read to done, follow-up true after a reply" "new to done, expired" "read to done, expired, no reply, notice sent" "refused: ack of an unread message" "refused: read by a non-recipient" "refused: backward moves" "refused: ack with follow-up and no reply" "refused: caller-set stamps" "refused: missing required fields" "refused: malformed file in every subcommand" "refused: size cap" "refused: invalid names and ids" "race: one winner" "race: non-atomic claim detected" "worktree: one shared mailbox"; do printf "%s\n" "$out" | grep -qxF "ok: $l" || exit 1; done`
- `m="$(cd "$(git rev-parse --git-common-dir)/.." && pwd)/.sdlc/messages" && b=$(ls -laR "$m" 2>&1; git ls-files --others --exclude-standard) && python3 plugins/sdlc-lite/scripts/messages.py selftest >/dev/null && test "$(ls -laR "$m" 2>&1; git ls-files --others --exclude-standard)" = "$b"`
- Observable: the verifier copies `messages.py` to a temp dir and injects two defects, one at a time: (a) `send` writes the current time into `read_time`; (b) the default claim becomes copy then delete. For each defect, the copy's selftest exits non-zero and prints a `messages selftest: FAIL:` line naming the failed case (expected: `create` for a, `race: one winner` for b). The verifier states what it injected and which case failed.
- `test -f plugins/sdlc-lite/scripts/messages.py && ! grep -q "$(printf "\xe2\x80\x94")" plugins/sdlc-lite/scripts/messages.py`
- (guard) `out=$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF plugins/sdlc-lite/scripts/messages.py ); test -z "$out"`
