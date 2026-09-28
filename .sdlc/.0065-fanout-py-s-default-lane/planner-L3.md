<!-- role=planner level=L3 model=fable effort=xhigh -->
## Goal
Every fanout lane driver runs with `SDLC_ROLE=conductor`, so `hooks/block-publish.sh` guards the Claude sessions a lane launches, the fanout selftest stub proves a driver sees it, and no doc still says only `scripts/run.sh` sets it.

## Step 1: Set SDLC_ROLE=conductor in the fanout lane env, prove it in the selftest stub, repair the docs
level: L2
### Do
- `plugins/sdlc-lite/scripts/fanout.py`, `run_ticket` (the `env = dict(ENV, ...)` call near line 382): add `SDLC_ROLE='conductor'` next to `SDLC_HEADLESS='1'`. Nothing else in the env changes. `scripts/run.sh` line 113 still sets `SDLC_ROLE="$role"` on every role run, so roles the lane conductor spawns keep their own role name.
- Same file, module docstring, the driver env list near line 36: after `SDLC_HEADLESS=1 (hooks/block-background.sh denies run_in_background)` add `SDLC_ROLE=conductor (hooks/block-publish.sh blocks git push, gh writes, and package publishing in the Claude sessions the driver launches)`. The `--driver` help near line 658 lists no env; leave it.
- Same file, the selftest `STUB` near line 504: next to the `SDLC_HEADLESS` line add `[ "${SDLC_ROLE:-}" = conductor ] || { echo "SDLC_ROLE not conductor" >&2; exit 1; }`.
- `plugins/sdlc-lite/agents/conductor.md` line 24: replace "and only `scripts/run.sh` sets it. This is by design: the hook guards role runs only." with wording that says `scripts/run.sh` sets it per role run and `scripts/fanout.py` sets it to `conductor` for every lane driver, so a lane conductor is guarded, while an interactive session has no `SDLC_ROLE`. Keep the closing sentence about the AskUserQuestion approval. The line must still contain `block-publish` and the word `fanout`.
- Repo-root `CLAUDE.md`: the `hooks/block-publish.sh` bullet (line 23): "(`SDLC_ROLE`, set by run.sh per role run and by fanout for lane drivers)"; the `hooks/block-background.sh` bullet (line 24): "(`SDLC_ROLE` set by run.sh or fanout, or `SDLC_HEADLESS=1`)"; the `scripts/fanout.py` bullet (line 30): the driver "gets `FANOUT_*` env, `SDLC_HEADLESS=1`, and `SDLC_ROLE=conductor`, so `hooks/block-publish.sh` guards the Claude sessions it launches". Leave "Your own session is not affected" as is.
- `.claude/agents/sdlc-lite-author.md` does not repeat the claim (checked: its `SDLC_ROLE` mention on line 30 is about block-background); change nothing there unless you find one.
- `plugins/sdlc-lite/skills/fanout/SKILL.md` lists no driver env and `plugins/sdlc-lite/skills/file/SKILL.md` describes the user's own session: leave both unchanged. Do not touch `plugins/sdlc-lite/hooks/`.
- No em dashes. Do not commit.
### Acceptance criteria
- `grep -Eq "SDLC_ROLE=['\"]conductor['\"]" plugins/sdlc-lite/scripts/fanout.py` (red now: fanout.py has no `SDLC_ROLE`)
- From the repo root, the stub refuses a missing role: `d="$(mktemp -d)" && mkdir "$d/a" && python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import fanout; sys.stdout.write(fanout.STUB)" > "$d/stub.sh" && ! (cd "$d" && env -u SDLC_ROLE SDLC_HEADLESS=1 FANOUT_TICKET=T-0001 FANOUT_SLUG=a FANOUT_ROOT="$d" bash stub.sh)` (red now: the stub exits 0 without `SDLC_ROLE`)
- (guard) From the repo root, the stub still passes with the role set: `d="$(mktemp -d)" && mkdir "$d/a" && python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import fanout; sys.stdout.write(fanout.STUB)" > "$d/stub.sh" && (cd "$d" && SDLC_ROLE=conductor SDLC_HEADLESS=1 FANOUT_TICKET=T-0001 FANOUT_SLUG=a FANOUT_ROOT="$d" bash stub.sh)`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and prints `fanout selftest: PASS` (after the step this proves the lane env carries `SDLC_ROLE=conductor`, since the stub now refuses without it)
- `sed -n '2,/^"""$/p' plugins/sdlc-lite/scripts/fanout.py | grep -q 'SDLC_ROLE=conductor'` (red now: the docstring's driver env list lacks it)
- `grep 'block-publish' plugins/sdlc-lite/agents/conductor.md | grep -q 'fanout'` (red now: line 24 names only run.sh)
- `! git grep -n 'only .scripts/run.sh. sets it' -- ':!.sdlc'` (red now: conductor.md line 24 matches; `.sdlc` is excluded because the ticket quotes the phrase)
- `grep 'block-publish.sh' CLAUDE.md | grep -q 'fanout'` (red now)
- `grep 'scripts/fanout.py' CLAUDE.md | grep -q 'SDLC_ROLE=conductor'` (red now)
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/hooks plugins/sdlc-lite/skills/file/SKILL.md`
- (guard) No em dash on any added line: `! git diff HEAD -- CLAUDE.md .claude plugins/sdlc-lite | grep '^+' | grep -v '^+++' | grep -q $'\xe2\x80\x94'`
- (guard) `plugins/sdlc-lite/scripts/check.sh` shows no new findings versus the base commit: run the same command in a `git worktree add <tmp> HEAD` copy and compare (exit 0 at HEAD now, about two minutes; the `claude plugin validate` warning about CLAUDE.md appears in both).

## Risks
`hooks/block-publish.sh` is a Claude Code PreToolUse hook, so `SDLC_ROLE=conductor` guards only the Claude sessions a driver launches (the default conductor and every `run.sh` role under it); a custom `--driver CMD` that runs `git push` straight from bash is not blocked, and only its author and the prompt govern that. `skills/file/SKILL.md` line 18 ("only fires when `SDLC_ROLE` is set by `scripts/run.sh`") and the comments at the top of both hooks stay incomplete by the ticket's own constraints (the user's session remains unguarded, and the hooks are not to change); a follow-up may reword them. `block-background.sh` now reports role `conductor` inside a lane instead of only `SDLC_HEADLESS=1`, with no behavior change.
