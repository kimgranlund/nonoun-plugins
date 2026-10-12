<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
`fanout.py settle <integration> --forward --gate CMD...` merges main into a diverged integration branch under the merge lock, regenerates the roadmap and router files, union-merges `notes.md`, runs the T-0481 cover gate at the new tip, and fast-forwards main only on green, while a plain `settle` still refuses a diverged branch.

guard timeout: 800

## Step 1: settle --forward with regenerate, union notes, cover, fast-forward
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Implementation targets. All are in `plugins/sdlc-lite/scripts/fanout.py` unless named otherwise: `cmd_settle` (about :2418), `cmd_cover` (about :2514), the settle argparse block (about :4781) and `USAGE` (about :4750). Design context: `docs/planning/merge-ops-and-queue.md` sections (2), (4), (6) and its Interfaces line for `settle`. Where the handoff and the design differ, the handoff wins (see 2 and 3).

1. Flags on the settle parser: `--forward` (store_true); `--gate CMD` (append); `--lanes-dir DIR` (default: the integration worktree's parent, as cover); `--gate-need [PREFIX::]RES=N` (append); `--no-gate-lock`; `--allow-empty-gate`. The extra flags exist because the cover helper reads `gate_needs_of(a)`, `a.no_gate_lock`, `a.allow_empty_gate` and `a.lanes_dir`. If `--forward` is given without a `--gate`, exit 2 with a message naming `--gate`, so a fast-forward is never ungated (design Risks, line 77). Update `USAGE` to `fanout.py settle <integration> [--root .sdlc] [--require-covered] [--forward --gate CMD... [--lanes-dir DIR] [--gate-need ...] [--no-gate-lock] [--allow-empty-gate]]`. Name T-0489 in the cmd_settle docstring.

2. Lock. `MergeLock` (about :1222) is a non-reentrant `threading.Lock` plus flock, and `cmd_cover` takes it at the top of its body. Extract cover's body after the lock (from `to = git_out(wt, 'rev-parse', 'HEAD')` through the ledger commit) into a lock-free `def cover_at(...)` that returns `(rc, to, frm, merges, ledger)`. `cmd_cover` keeps its preflight, wraps `cover_at` in `MergeLock(lanes_dir / 'merge.lock')`, and keeps its output and exit codes unchanged. `settle --forward` takes that same `merge.lock` once and calls `cover_at` inside it. Do not add the design's `settle.lock`: the handoff says "reuse the merge lock".

3. Forward path. It runs only when `--forward` is given and the integration branch is neither an ancestor of HEAD nor a fast-forward of it (`git merge-base --is-ancestor HEAD <integration>` fails). Every other case keeps today's code path unchanged, so plain `settle` on a diverged branch still exits 2 with `not a fast-forward`.
   - Find the integration worktree the way `cmd_cover` does. If there is none, exit 2. If its tracked status is dirty (`git status --porcelain --untracked-files=no`), exit 2.
   - Under the lock, re-read `refs/heads/<head>`. In the integration worktree, run `git merge --no-ff --no-commit <that sha>`.
   - Conflicted paths: `git diff --name-only --diff-filter=U`.
   - The generated set is resolved with `tickets.layout_paths(root)` and `tickets.router_files(root)`, where `root` is `<wt>/<rel>` for the ticket root `--root` relative to the toplevel. It holds `.roadmap`, `.notes`, and every path `router_files` returns (AGENTS.md and CLAUDE.md, plus the tickets/ and topics variants).
   - If any conflicted path is outside that set, run `git merge --abort` and confirm there is no `MERGE_HEAD`. Print `fanout: settle --forward: conflict outside the generated files: <paths>; main, <integration> and the tree are unchanged` on stderr and exit 2.
   - The `check.sh` header comment is not in the generated set; see Assumptions.
   - `notes.md` conflict: write `git merge-file -p --union` over its stages `:1:`, `:2:` and `:3:` (read with `git show`) and `git add` it. An add/add with no stage 1 uses an empty base file.
   - roadmap and router conflicts: `git checkout --ours -- <path>` to drop the markers.
   - Then regenerate unconditionally, clean merge included: run `tickets.py --root <wt>/<rel> roadmap` as a subprocess in the worktree. If it fails, run `git merge --abort` and exit 2 with its message. Then `git add` every generated path that exists.
   - Commit with the subject `settle --forward: <head> <sha7> into <integration>`. It must not match `MERGE_SUBJECT` (`Merge (\S+): (T-\d+)`), or cover would list a phantom ticket.
   - Call `cover_at` at the new tip. Red: print what `cmd_cover` prints (`red: ...` and the `git bisect start <to> <from> --first-parent` line) and exit 1. Main stays unmoved, and the forward-merge commit plus the red ledger commit stay on the integration branch.
   - Green: release the lock. If `--require-covered` is also set, apply it now. Then continue into the existing `git merge --ff-only <integration>` and `close_lane` code, which prints `settled: ...`.
   - Do not write the design's `land.jsonl` journal line (see Risks).

4. Selftest. Add a case after case 28's block (before case 29) with every label prefixed `T-0489`. Do not renumber other cases. Write it first and run `fanout.py selftest` on the unmodified code. Record in the builder result that it fails today with exit 2 and `not a fast-forward of main`, or with the unknown `--forward` flag. Fixture:
   - `sized_repo(..., ['L1', 'L1'], {'.gitignore': gi})`. `make_repo` writes no `roadmap.md` and no `.sdlc/AGENTS.md`.
   - `make_branch` a `worktree-T-0001-solo` branch, then `fanout.py land` it with `--integration fanout/x --lanes-dir <tmp> --base main --gate true`, as case 34 does. Close regenerates `roadmap.md` and `.sdlc/AGENTS.md` on the integration branch.
   - On main, run `tickets.py new` to file T-0003 and commit it. This regenerates both files there, so the merge hits add/add conflicts on both. That is the conflict the case must exercise.
   - Then `settle fanout/x --forward --gate true`.

   Assertions:
   - exit 0 and `settled` in stdout.
   - main equals the archive ref's commit (the branch is deleted by `close_lane`; use `archived`).
   - `git show main:.sdlc/roadmap.md` lists T-0001 as done and T-0003 as proposed.
   - `tickets.py --root .sdlc check` on main exits 0.
   - The newest `gate-ledger.jsonl` entry has rc 0 and `to == main^1`, and `git diff --name-only <to> main` lists only the fixture repo's ledger file, `<rel>/gate-ledger.jsonl` with `<rel>` its ticket root (the path `cmd_cover` commits).

   Negative controls, on fresh branches or repos:
   - `README.md` edited on both sides: exit 2 with `README.md` in stderr; `git status --porcelain` empty in both the checkout and the integration tree; no `MERGE_HEAD` (`git rev-parse -q --verify MERGE_HEAD` fails in the integration tree); main sha and branch tip unchanged.
   - Plain `settle` on a diverged branch: exit 2 with `not a fast-forward`.
   - `--gate false`: exit 1; main unmoved; the forward-merge commit is on the integration branch (an ancestor of its tip, with the subject from 3).
   - `--forward` with no `--gate`: exit 2.

5. Docs.
   - `docs/references/sdlc-internals.md`: in the `settle` paragraph (about :155), add a description of `settle <integration> --forward` covering the flags, the generated set, the union of notes, the refusal, cover at the new tip and the ff-only.
   - `plugins/sdlc-lite/skills/fanout/SKILL.md`: near :51 to :53, add one sentence that a diverged integration branch, after the user picks it, takes `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py settle <integration> --forward --gate "<cmd>"...` instead of a hand merge.
   - Both files must contain the literal `settle <integration> --forward`.
   - Only add text. Do not replace it: check.py item 24 pins fanout SKILL.md phrases, and check.py:1042 pins `fanout.py settle` in run-rules.md.

Contract dependents (from `git grep -n settle` over plugins, docs and check.py):
- Case 28 and the T-0481 case 34 call `settle` without the new flags and must stay green.
- `cmd_cover`'s output is pinned by case 34. `cover_at` must keep its text and ledger shape.
- check.py:204 and :1042 pin `fanout.py settle` in run-rules.md, which is left untouched.
- `report.py` reads `land.jsonl`, which this step does not write, so it is left untouched.

Depends on: none.

Validation scope: the T-0489 selftest case, `fanout.py selftest`, `tickets.py selftest`, `check.py`. The full `check.sh` belongs to this wave's `fanout.py land` gates and is not run here. Leave scratch only under `$SDLC_TMP_WORKTREES`. Never delete anything.
### Acceptance criteria
- (red) `python3 plugins/sdlc-lite/scripts/fanout.py settle --help | grep -qF -- --forward`
- (red) `grep -qE '^def cover_at\(' plugins/sdlc-lite/scripts/fanout.py`
- (red) `grep -qF 'T-0489' plugins/sdlc-lite/scripts/fanout.py`
- (red) `grep -qF -- 'settle <integration> --forward' docs/references/sdlc-internals.md`
- (red) `grep -qF -- 'settle <integration> --forward' plugins/sdlc-lite/skills/fanout/SKILL.md`
- The builder result records the T-0489 case observed red on the unmodified `fanout.py` (exit 1, `T-0489` labels under `these did not hold:`).
- Observed negative control: in a `git worktree add --detach` copy of the built tree under `$SDLC_TMP_WORKTREES`, make the forward path skip the `tickets.py roadmap` regeneration (or the notes union), then run `fanout.py selftest`. It must exit 1 and list at least one `T-0489` label. The unmodified built tree passes.
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE 'plugins/sdlc-lite/scripts/fanout\.py|plugins/sdlc-lite/skills/fanout/SKILL\.md|docs/references/sdlc-internals\.md'`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py && python3 plugins/sdlc-lite/scripts/tickets.py selftest`

## Assumptions
- The handoff's "reuse the merge lock" overrides the design's new `settle.lock`, and `cmd_cover` cannot be called under a held `MergeLock`: verified at fanout.py:1222-1239 (a `threading.Lock` plus `fcntl.flock`, non-reentrant) and in `cmd_cover`, which opens `MergeLock(lanes_dir / 'merge.lock')` itself.
- Generated files are regenerated by `tickets.py roadmap`, which calls `write_roadmap`, which calls `write_router`, covering roadmap.md and every `router_files` path: verified at tickets.py:1450-1455, :1581-1593 and :2231-2240.
- The `check.sh` header comment is refused like any non-generated path, although the handoff lists it with the generated files. Evidence: no script generates it (`tickets.py` has no `check.sh` writer), and `docs/planning/merge-ops-and-queue.md` section (2) calls it hand-edited residue that "stay[s] with a person". The done-when never exercises it.
- The done-when's "main equals the integration tip ... one ledger entry has `to` equal to that tip" cannot hold literally, because cover commits the ledger after the gates and moves the tip past `to`. The selftest asserts the honest form instead: main equals the archived tip, the newest entry's `to` is `main^1`, and only the ledger changed since `to`. This is the same rule `require_covered` encodes (fanout.py, `require_covered`).
- The fixture hits add/add conflicts on roadmap.md and `.sdlc/AGENTS.md`, because `make_repo` writes neither and both sides generate them: verified at fanout.py:2707-2720.
- Probes at base HEAD 5c42e976: all five `(red)` criteria exit 1 for the right reason (no flag, def, label or phrase yet). The scope guard exits 0, and its form with an injected `README.md` went red (exit 1). check.py ok in 10 s, `tickets.py selftest` PASS in 86 s, `fanout.py selftest` PASS in 254 s, so the guard timeout is 800.
- Replan by planner L3 for the plan-review refusal: the only change from planner-L2.md is the ledger assertion in step 1, Do item 4, which named the fixture repo's ledger with a `.sdlc/` prefix that `steps.py lint` resolves against this tree. Verified with `steps.link_findings` on a split copy of the revised step (no finding) and on the refused step 1 handoff (the same finding as the refusal record). Re-probed at 5c42e976: the five `(red)` criteria exit 1, the scope guard exits 0 and goes red with an injected `README.md`, `check.py` plus `tickets.py selftest` pass in 70 s, `fanout.py selftest` passes in 238 s, `specgate.py check` and `steps.py lint` are ok.

## Risks
- The handoff lists the `check.sh` header comment among the generated files. The plan refuses it instead, per the design. If the maintainer wanted it auto-resolved, a follow-up ticket adds that rule.
- The design's `land.jsonl` journal line for settle is not built. `report.py` reads `land.jsonl`, and a new line shape is an unchecked dependent.
- `fanout.py selftest` took 254 s here, and host load varies. A heavily loaded host could approach the 800 s guard timeout.
- After `git checkout --ours`, the regeneration rewrites the roadmap and router files from the merged ticket set. If `tickets.py roadmap` refuses on ticket problems in the merged tree, settle aborts with exit 2, and that is the intended outcome.
- Cross-wave ordering of settles (design section 2) is not built. Two concurrent settles into different integration branches only serialize through each branch's own merge.lock.
- `steps.py lint` warns that the criterion recording the T-0489 case observed red cites a count without a named command. It is cosmetic and is kept unchanged, as the plan review asked.
