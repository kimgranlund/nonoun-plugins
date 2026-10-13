<!-- role=architect level=L1 model=opus effort=xhigh -->
## Approach
This is a triage, not a build design. I skipped the two-plane decompose and coverage check because the handoff asks for a decision list, not a structural breakdown.

I checked each observation against main at 0.22.7, `git log v0.22.6..v0.22.7` and the open roadmap. Only three tickets are open (T-0521, T-0522 and this one), so no open ticket already covers an observation. Only one observation is fixed by the 0.22.7 release, and one more was fixed before maison's 0.22.6:

- Item 7 was fixed in 0.22.7 by T-0505. It is Claude-only and warns by default. Maison cannot use it until it upgrades after T-0439.
- Item 16 was fixed in 0.22.5 by T-0451, so maison already has it.

Four items are declined:
- **13:** the brief already carries the Base sha and tmp prefix lines, and a sub-agent's environment comes from the host.
- **14:** the builder contract already allows WIP commits when the brief asks.
- **19:** this is host behavior plus the consent rule working as designed.
- **27:** git log is the delivery record, and an umbrella ticket closes with `--reason`.

The other 24 items group into 7 tickets, all size L2. Five of them edit `plugins/sdlc-lite/scripts/tickets.py` (A, B, C, D, G). Run those one after another in the order A, C, B, G, D, or in one lane. E and F touch other files and can run in parallel.

The reply draft is at `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.sdlc/0525-maison-0546-triage/author-reply.draft.md`. It has 30 lines numbered 1 to 30, no em dashes, and every accepted line names a group letter A to G. The conductor replaces each letter with the T-NNNN it files.

## Interfaces
Each proposed ticket below has a letter, title, size, the observations it covers, the files it changes, and a runnable done-when.

**A. Claim and release commands, plus claim lint.** Size L2. Observations 1, 2, 3, 22.
- **Files:** `plugins/sdlc-lite/scripts/tickets.py`: a new `claim <id> --by <agent> [--handover --reason TEXT]` and `release <id>`; `problems` and `cmd_check` warnings; the "Claim a ticket" text in `ROUTER_PROCEDURES` (around line 1558). Also `plugins/sdlc-lite/skills/ticket/SKILL.md`.
- **Behavior:**
  - `claim` writes `status: claimed` and `claimed_by: <agent> <YYYY-MM-DD>` directly after `created:`, then runs roadmap.
  - `--handover` replaces the value and appends one dated body line.
  - `check` warns on a trailing comment on the claim line, on a claim line out of place, and on a claim older than `claim_days:` (config, default 7) when the folder has no running attempt.
  - When a ticket problem makes `new` refuse, the message names that ticket and the one-line fix.
- **Done-when:** `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with these new cases:
  - `claim` on a fixture puts the line after `created:` and regenerates the roadmap.
  - A claim line with a trailing comment produces a warning naming the ticket. The same fixture without the comment produces none (negative control).
  - A 10-day-old claim with no running attempt is listed. The same claim beside a running attempt is not.
  - `new` succeeds beside a ticket that has both `status: claimed` and `claimed_by:`.

**B. Detect delivered and superseded open tickets.** Size L2. Observations 21, 23, 24, 25, 26.
- **Files:** `plugins/sdlc-lite/scripts/tickets.py` (field validation, `cmd_check`, roadmap row), `plugins/sdlc-lite/skills/ticket/SKILL.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md` (field list).
- **Behavior:**
  - `check` lists every open ticket whose id starts a commit subject (`T-NNNN:`) on the default branch.
  - A new optional field `successor: <T-NNNN | <repo>:T-NNNN>` covers four cases with one record: superseded, delivered under another ticket, verified by an integration ticket, and fixed in another repository.
  - When a local successor is done, `check` prints the ready-to-run `close <folder> --reason "..."` line. A cross-repository successor is shown but not resolved.
- **Done-when:** `tickets.py selftest` exits 0 with these new cases:
  - In a git fixture, a commit `T-0002: x` on main makes `check` list T-0002. The same commit on an unmerged branch lists nothing (negative control).
  - `successor: T-0003` with T-0003 done prints the close line. With T-0003 open it prints nothing.
  - `successor: maison:T-0158` is accepted and `successor: banana` is rejected.

**C. Close references, router links, launcher and root guard.** Size L2. Observations 4, 5, 6, 12.
- **Files:** `plugins/sdlc-lite/scripts/tickets.py`: the reference scan (lines 859-868), `ROUTER_PROCEDURES` (around line 1558), `write_router` (around line 1745), `cmd_check`, `main` (around line 5461). Also `plugins/sdlc-lite/skills/ticket/SKILL.md` (config keys).
- **Behavior:**
  - The scan that runs with ignore rules off covers the whole `<root>`, not only the ticket root. A gitignored `.sdlc/AGENTS.md` is then found and rewritten.
  - `check` warns on a relative link in `<root>/AGENTS.md`, outside the managed block, whose target is missing but whose dot-folder exists.
  - A new config key `tickets_cmd:` replaces the raw `tickets.py` command in the generated procedures. The Close steps name `--rewrite-refs`.
  - Every subcommand except `new` refuses a `--root` that holds no `config`, `roadmap.md` or ticket folder.
- **Done-when:** `tickets.py selftest` exits 0 with these new cases:
  - Fixture: `.sdlc/` gitignored, `ticket_root: tickets`, and `.sdlc/AGENTS.md` citing `tickets/0002-b/handoff.md`. `close 0002-b --dry-run` lists that file and `--rewrite-refs` rewrites it. The same fixture against HEAD's script lists nothing (negative control).
  - With `tickets_cmd: python3 .sdlc/tickets-run.py`, the managed block contains that string and no bare `tickets.py --root` line.
  - `tickets.py --root <empty dir> check` exits nonzero.

**D. Lane record on the ticket.** Size L2. Observations 15, 30, and 31. Item 31 has no line in the reply; see Risks.
- **Files:**
  - `plugins/sdlc-lite/scripts/lanes.py` (`open_lane`, `close_lane`, `list_lanes` around line 978)
  - `plugins/sdlc-lite/scripts/tickets.py` (a `branch:` field, shown on the roadmap and router active line; an "Open a lane" procedure)
  - `plugins/sdlc-lite/scripts/board.py`
  - `plugins/sdlc-lite/skills/handoff-format/run-operations.md`
- **Behavior:**
  - `lanes.py open --ticket` writes `branch:` and `close` removes it.
  - `list --all` matches a manual worktree to its ticket by `branch:` and shows the ticket's newest verifier verdict, so verified, unmerged work is visible.
  - `lanes.py open` already applies the claim rule, which covers "dispatch on an unclaimed ticket" once lanes open through it.
- **Done-when:** `python3 plugins/sdlc-lite/scripts/lanes.py selftest` and `tickets.py selftest` exit 0 with these new cases:
  - A manual worktree on `fix-0520`, plus a ticket with `branch: fix-0520` and a passing `verifier-L2.md`, gives a `list --all --json` row with ticket `T-0520` and verdict `pass`. Without the `branch:` line the row has no ticket (negative control).
  - `open --kind solo --ticket T-0001` writes `branch: lane/...` and `close` removes it.

**E. Run records: retry names, filer prune, empty solo.** Size L2. Observations 8, 9, 28.
- **Files:** `plugins/sdlc-lite/scripts/dispatch.py` (`next_stem` and `agent_name` around lines 287 and 803; `queue_prune` around line 1054; prune docs at lines 109-113), `plugins/sdlc-lite/scripts/solo_run.py` (around lines 609-630).
- **Behavior:**
  - The attempt counter also counts attempt records with no result, so a retry is named `-2` the same way the host names it.
  - A filer is queued for prune even when it has follow-ups, because its follow-ups are its output and `close` consumes them.
  - A solo whose result text is empty, or that leaves no result file, is a failed run.
  - A solo refuses a handoff that is still the unfilled template.
- **Done-when:** `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` and `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exit 0 with these new cases:
  - Two prepares on a dir whose first attempt left no result file print `...-L4` and then `...-L4-2`. HEAD's script prints the same name twice (negative control).
  - A filer record whose result has a non-empty `## Follow-ups` prints `prune: <name>`.
  - A result event with empty text exits 1 and prints `FAILED`.
  - A solo on a template-equal handoff refuses.

**F. Step tooling and long suites.** Size L2. Observations 10, 11, 20.
- **Files:** `plugins/sdlc-lite/scripts/steps.py` (`split` around lines 1823-1864, `swap` around line 3277), `plugins/sdlc-lite/agents/verifier.md` (rule 5), and the generated agent definitions (regenerated, never edited by hand).
- **Behavior:**
  - `split --supersede` renames a step dir that holds role output to the next free `step-<n>.superseded-<k>`, then splits.
  - `swap` accepts a solo task folder, using the solo result in place of the builder result.
  - The verifier rule says to shard a suite that cannot finish within the 600000 ms foreground cap.
- **Done-when:** `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with these new cases:
  - `split --supersede` on a `step-2` holding `builder-L2.md` moves it to `step-2.superseded-1` and writes a new `step-2`. Without the flag it still refuses and writes nothing (negative control).
  - `swap` on a solo dir with `solo-L2.md` and a plan-defect verifier fail applies the swap.

  Also, `grep -n shard plugins/sdlc-lite/agents/verifier.md` prints a line and `bash plugins/sdlc-lite/scripts/check.sh` passes, which includes generated-agent parity.

**G. Writing rules for work records, and a placeholder gate at close.** Size L2. Observations 17, 18, 29.
- **Files:** a new `plugins/sdlc-lite/skills/handoff-format/references/writing-rules.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md` (link), the `ROUTER_TEMPLATE` link in `tickets.py`, and `cmd_close` reusing `placeholder_problems` (around line 1405).
- **Behavior:**
  - The new reference holds controlled language and the patterns maison listed: checklist, dependency, decision, criterion, status line, open question, lane.
  - It adds a rule that `notes.md` never states a ticket's status and cites the ticket instead.
  - `close` refuses a handoff that still holds template placeholder text, unless `--reason` is given.
- **Done-when:**
  - `test -f plugins/sdlc-lite/skills/handoff-format/references/writing-rules.md`
  - `grep -n writing-rules.md plugins/sdlc-lite/skills/handoff-format/SKILL.md` prints a line.
  - `tickets.py selftest` exits 0 with a new case: `close` on a fixture holding the bug template's Repro prompt line exits nonzero and names the line. The same fixture filled in closes (negative control).
  - `python3 scripts/check-packaging.py` passes.

## Constraints and assumptions
- Only T-0505 (item 7) lands in 0.22.7: verified by `git tag --contains a1b7576f` printing v0.22.7 first, and by reading the diffs of `dispatch.py`, `steps.py` and `solo_run.py` since v0.22.6, which add nothing for the other items.
- T-0451 (`lanes.py list --all`, item 16) first shipped in v0.22.5: verified by `git tag --contains e13576d1`.
- No open ticket covers any item: verified from the roadmap rows that are not done or dropped (T-0521, T-0522, T-0525).
- The 0.22.6 ticket templates already list `claimed` in the `status:` comment: verified with `git show v0.22.6:.../templates/bug.md`. Maison's comment comes from older stamped tickets. Maison's reason for `new` refusing on `status: claimed` was not reproduced, so A's done-when uses a fixture instead.
- `.sdlc/` is gitignored in maison: verified with `git check-ignore -v`. The ignore-off scan covers only the ticket root (`tickets.py:864-868`), so `.sdlc/AGENTS.md` is never scanned. That explains item 5.
- The filer never reaches the prune queue: `queue_prune` skips any result whose `## Follow-ups` is not None (`dispatch.py:1063`, `:1036`). That a filer has no later continuation that needs it alive is unverified.
- A solo with empty result text exits 0 with no file: verified by reading `solo_run.py:609-623`.
- Item 9's cause is unverified. The assumption is that `next_stem` counts result files only, so a failed attempt with no result file reuses the same name. The planner confirms this with a fixture before building.
- The sub-agent brief already carries Base sha and tmp worktree lines in 0.22.6 (verified: `Base sha: %s` appears in the v0.22.6 `dispatch.py`), and `.nvmrc` not carrying over is documented at `dispatch.py:120`.
- The builder may make WIP commits when the brief asks: verified at `plugins/sdlc-lite/agents/builder.md:18`.

## Rejected alternatives
- **A red-checkpoint mode for an uncommitted lane (14):** WIP commits already give each step a clean tree, and the phase is read from the tree by design (T-0473).
- **A `delivered:` sha field (27):** it duplicates git history. B reads the commit subjects instead.
- **Separate `verified_by:`, `superseded_by:` and `delivered_under:` fields (23-26):** one `successor:` field plus `close --reason` records all four cases.
- **A `lanes` command in a new script (15, 16):** `lanes.py` already owns the lane lifecycle, so D extends it.
- **Exporting Node and env vars to sub-agents (13):** the host gives a sub-agent its environment, and `prepare` cannot set it.
- **Queuing the filer for prune from `close` (8):** the agent should be stopped soon after its run, not when close happens much later. I kept it in `record`.
- **The decompose manifest and coverage check:** the deliverable is a decision list with no structure to cover.

## Risks
- `observations.md` has 31 items; line 40 is item 31: a `branch:` field, joining lanes to tickets, and dispatch on an unclaimed ticket. The frozen done-when asks for 30 lines, so the draft has 30. D covers item 31. Add `31. accepted as sdlc-lite D` before sending the reply, because maison's own done-when asks for one line per observation.
- Five tickets edit `tickets.py`. Run in parallel lanes, they will conflict.
- Item 3's trigger was not reproduced. If maison's refusal comes from something other than ticket problems (for example, a parse quirk of a comment on the claim line), A's fixture may pass without fixing their case.
- Item 9's root cause is inferred, not reproduced.
- Exempting the filer from the follow-ups skip in E may be wrong if a parent expects to continue a filer after loose ends.
- Maison stays on 0.22.6 until its T-0439 closes, so none of this reaches it before then.

## Carry forward
- Reply draft: `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.sdlc/0525-maison-0546-triage/author-reply.draft.md` (30 lines, letters A-G, item 31 missing on purpose).
- Gitignored ref-scan gap: `plugins/sdlc-lite/scripts/tickets.py:864-868` (the ignore-off grep is limited to `rel`, the ticket root).
- Generated Claim and Close procedures: `plugins/sdlc-lite/scripts/tickets.py:1558` (`ROUTER_PROCEDURES`); router writer at `:1745`.
- `new` refuses on any ticket problem: `plugins/sdlc-lite/scripts/tickets.py:1878-1880`.
- Placeholder lint to reuse at close: `plugins/sdlc-lite/scripts/tickets.py:1405` (`placeholder_problems`).
- Filer never pruned: `plugins/sdlc-lite/scripts/dispatch.py:1054-1068` (`queue_prune`), `:1036` (`follow_up_pending`).
- Agent naming: `plugins/sdlc-lite/scripts/dispatch.py:287` (`agent_name`), `:802-803` (`next_stem`).
- Empty solo result treated as success: `plugins/sdlc-lite/scripts/solo_run.py:609-623`.
- `split` refusal on role output: `plugins/sdlc-lite/scripts/steps.py:1863`; `swap` needs a builder and verifier result: `:3291-3293`.
- `lanes.py list` rows: `plugins/sdlc-lite/scripts/lanes.py:978-990`; manual worktrees are listed with `--all`.
- Verifier foreground cap rule: `plugins/sdlc-lite/agents/verifier.md:22`. Builder WIP-commit rule: `plugins/sdlc-lite/agents/builder.md:18`.
- Handoff edit hook (T-0505, 0.22.7, warn by default): `plugins/sdlc-lite/hooks/warn-handoff-edit.sh:19`.
- Release ids cited in the reply: T-0505 first tagged v0.22.7, T-0451 first tagged v0.22.5 (`git tag --contains`).
- Maison `.sdlc/` is gitignored at `/Users/kimgranlund/Projects/maison/ui-kit-maison/.gitignore:6`.
