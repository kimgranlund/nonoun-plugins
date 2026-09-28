## Task goal
`steps.py split --only N` runs that step's `(guard)` criteria against the current tree before writing its handoff, and refuses with a `plan defect` line when a guard is red now, so a plan whose guard cannot pass is caught before the build instead of by the verifier.

Done when: `split --only N` executes each runnable `(guard)` command span of step N (skipping spans that reference `HEAD^1` or contain a `<placeholder>`, each under a timeout), refuses and writes nothing on a red or timed-out guard with `plan defect` as the last stderr line naming the criterion, the full `split` (no `--only`) and `lint` still execute nothing, `steps.py selftest` proves each case (red guard refuses, green guard passes, HEAD^1 and placeholder guards skipped, timeout refuses, full split does not execute), and the docs that describe `split` (the `steps.py` usage text, CLAUDE.md, `.claude/agents/sdlc-lite-author.md`, `/chain` 4.2 and the plan-defect decision) say so. `scripts/check.sh` passes.

## Step 2: Document the guard run and add it to check.py's doc guard
level: L2
### Do
Describe the new behavior everywhere `split` is described, using the literal phrase `red guard` in each place:
- `CLAUDE.md` (repo root):
  - the `scripts/steps.py` Layout bullet: `split --only N` runs that step's `(guard)` command spans under `--guard-timeout` (default 300s) from the git toplevel, skipping `HEAD^1` and `<placeholder>` spans, and refuses on a red guard or timeout with a `plan defect:` last line; full `split` and `lint` execute nothing;
  - the Systems line that counts the code gates;
  - the "A plan defect goes to a replan" decision paragraph, which must say a red guard in `split --only` is a plan defect.
- `.claude/agents/sdlc-lite-author.md`: the plan-defect route bullet names the `split --only` red guard as a source.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: item 2 of section 4, the line starting `2. builder Status blocked`, says `--only N` runs that step's guards and that a red guard refusal is a `plan defect` handled like the section 3 split refusal. Optionally mention it in section 3 too, noting that the full split there executes nothing.
- `plugins/sdlc-lite/scripts/check.py`: add `'red guard': ('skills/chain/SKILL.md', 'scripts/steps.py')` to `PLAN_DEFECT_DOCS`.

Keep every existing phrase that check.py already guards: `plan defect`, `Plan review`, `no new findings`.
### Acceptance criteria
- `test -z "$(grep -L 'red guard' CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/skills/chain/SKILL.md)"`
- `grep 'A plan defect goes to a replan' CLAUDE.md | grep -q 'red guard'`
- `grep '^2\. builder Status blocked' plugins/sdlc-lite/skills/chain/SKILL.md | grep -q 'red guard'`
- `grep -q "'red guard'" plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) Running `plugins/sdlc-lite/scripts/check.sh` from the repo root exits 0.
