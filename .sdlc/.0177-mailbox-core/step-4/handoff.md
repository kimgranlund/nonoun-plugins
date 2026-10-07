## Task goal
`plugins/sdlc-lite/scripts/messages.py` runs a git-ignored `.sdlc/messages/` mailbox with a validated schema, an explicit new, read, done lifecycle, and a tested transition table, and `run.sh` prints a count notice before it launches a role.

## Step 4: ignore rules, onboard guidance, and docs
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 to 3, because the docs describe the built interface and the notice. T-0175 edits some of these files in parallel (`.sdlc/0175-ticket-root-router/planner-L3-2.md:253-284`), so edit only the places named here.

`.gitignore`: add the line `.sdlc/messages/` after `.sdlc/runtime/`.

`plugins/sdlc-lite/skills/handoff-format/SKILL.md`:
- In the Layout code block, add a line after `.sdlc/runtime/`, the block's last line: `.sdlc/messages/         git-ignored mailbox written by scripts/messages.py: new/, read/, done/ per receiver, shared by worktrees; never committed`. T-0175 inserts its lines before `.sdlc/runtime/`.
- In the fenced ignore list, add `.sdlc/messages/` after `.sdlc/runtime/`.
- Below the list, after the `.sdlc/runtime/` bullet, add this bullet: - `.sdlc/messages/`: the local mailbox written by `scripts/messages.py`; never committed, even when the trail is.
- No agent preloads this skill, so the Codex agents need no regeneration.

`plugins/sdlc-lite/scripts/onboard.py`:
- In `ROOT_AGENTS_TEMPLATE`, add the bullet ``- `.sdlc/messages/` is a local mailbox. Keep it in `.gitignore` and never commit it.`` right after the `.sdlc/roadmap.md` line (`onboard.py:252`).
- Mirror it byte for byte in `docs/specs/repo-onboarding/design.md` after line 261, because `onboard.py:228` says the template texts are copied byte for byte from that design.
- Keep `TEMPLATE_VERSION = 1`. An existing v1 block whose text differs from the template is row 6 `stale`, and the next setup replaces it (`onboard.py:552-580`).
- Contract dependents: the onboard selftest, run below. No other file pins the template text: `git grep` of the roadmap line finds only these two.

`docs/references/sdlc-internals.md`:
- Add an entry headed ``## `scripts/messages.py` `` between the `scripts/run.sh` entry and `## Feed`. Cover the subcommands, layout, root resolution, schema, lifecycle, reply rule, lock, trust rule, and selftest coverage, including the race negative control.
- Append one sentence on the notice to the `scripts/run.sh` entry.
- Touch nothing else in this file: T-0175 edits the tickets, board, fanout, and traces entries.

`docs/specs/ticket-stages/design.md`, Message bus section only:
- Add a status line right after the heading. It says the mailbox core is built in T-0177 (`scripts/messages.py` and the run.sh notice), and that the `messenger` agent (T-0178) and the entry files with the live run (T-0179) are pending.
- Replace "`re` (ticket id)" with wording that says `re` holds the id of the message being answered.
- In the transition table, name the command on every row: `messages.py send` or `reply` on create, with `protocol` added to its Stamped cell, and `messages.py expire` on both expiry rows.
- State the exact reply rule and the notice fields.
- Leave line 3 alone, because T-0175 rewrites it.

Leave `docs/README.md` and `docs/specs/ticket-stages/README.md` untouched. T-0175 rewrites their ticket-stages lines, and T-0179 owns the final status.

Write no em dash in any added line.
### Acceptance criteria
- `git check-ignore -q .sdlc/messages/new/bob/x.md`
- `grep -qx ".sdlc/messages/" plugins/sdlc-lite/skills/handoff-format/SKILL.md && grep -qE "^\.sdlc/messages/ +.*scripts/messages\.py" plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `a=$(grep -F "local mailbox" plugins/sdlc-lite/scripts/onboard.py) && printf "%s\n" "$a" | grep -qF ".sdlc/messages/" && test "$a" = "$(grep -F "local mailbox" docs/specs/repo-onboarding/design.md)" && python3 plugins/sdlc-lite/scripts/onboard.py selftest`
- `grep -qF "new message(s)" docs/references/sdlc-internals.md && awk '/^## .scripts\/run.sh.$/ {r = NR} /^## .scripts\/messages.py.$/ {m = NR} /^## Feed$/ {f = NR} END {exit !(r && m > r && f > m)}' docs/references/sdlc-internals.md`
- `grep -qF "messages.py expire" docs/specs/ticket-stages/design.md && grep -qF "T-0177" docs/specs/ticket-stages/design.md && ! grep -qF "(ticket id)" docs/specs/ticket-stages/design.md`
- (guard) `grep -qx "TEMPLATE_VERSION = 1" plugins/sdlc-lite/scripts/onboard.py`
- (guard) `test "$(sed -n 3p docs/specs/ticket-stages/design.md)" = "$(git show "$SDLC_BASE_SHA":docs/ticket-stages/design.md | sed -n 3p)"`
- (guard) `! git diff "$SDLC_BASE_SHA" -- .gitignore plugins/sdlc-lite/skills/handoff-format/SKILL.md plugins/sdlc-lite/scripts/onboard.py docs/specs/repo-onboarding/design.md docs/references/sdlc-internals.md docs/specs/ticket-stages/design.md | grep "^+" | grep -q "$(printf "\xe2\x80\x94")"`
- (guard) `out=$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.sh -e .gitignore -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e plugins/sdlc-lite/scripts/onboard.py -e docs/specs/repo-onboarding/design.md -e docs/references/sdlc-internals.md -e docs/specs/ticket-stages/design.md ); test -z "$out"`
