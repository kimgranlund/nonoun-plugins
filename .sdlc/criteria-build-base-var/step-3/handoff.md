## Task goal
A step's scope criteria compare against the tree the build started from, and that works whether or not anything gets committed later.

## Step 3: Planner rule, role prompts, docs, and check.py guard for SDLC_BASE_SHA
level: L2
### Do
- `plugins/sdlc-lite/agents/planner.md` rule 6: name `$SDLC_BASE_SHA` as the build-start base. run.sh exports it to builder and verifier: HEAD at the step's first builder run, kept in the step dir's `base-sha`, moved past a resync merge. `steps.py split --only` and `swap` set it too. Scope criteria (which files the step changed) use `git diff --name-only "$SDLC_BASE_SHA"` plus `git ls-files --others --exclude-standard`. They never use `git diff HEAD~1 HEAD`, because builders never commit except on Merge steps, and never a bare `git diff HEAD`, which goes vacuous once the work is committed separately.
- Rule 13: its `git diff --quiet HEAD -- <path>` becomes `git diff --quiet "$SDLC_BASE_SHA" -- <path>`.
- `plugins/sdlc-lite/agents/builder.md` item 8 and `plugins/sdlc-lite/agents/verifier.md` item 4: the pre-build HEAD is `$SDLC_BASE_SHA` (still `HEAD^1` on a merge step), e.g. `git worktree add --detach "$SDLC_TMP_WORKTREES/base" "$SDLC_BASE_SHA"`.
- `plugins/sdlc-lite/scripts/check.py`: add an `'SDLC_BASE_SHA'` entry to `PLAN_DEFECT_DOCS` covering `agents/planner.md`, `agents/builder.md`, `agents/verifier.md`, `scripts/run.sh`, and `scripts/steps.py`, and describe it in the docstring's item 5.
- Repo-root `CLAUDE.md` (run.sh and steps.py paragraphs, plus the plan-defect Decision where the planner rules are listed) and `.claude/agents/sdlc-lite-author.md`: describe `SDLC_BASE_SHA` and the `base-sha` file.
- No em dashes.
### Acceptance criteria
- `grep -qF 'git diff --name-only "$SDLC_BASE_SHA"' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'SDLC_BASE_SHA' plugins/sdlc-lite/agents/builder.md`
- `grep -qF 'SDLC_BASE_SHA' plugins/sdlc-lite/agents/verifier.md`
- `grep -qF 'SDLC_BASE_SHA' CLAUDE.md`
- `grep -qF 'SDLC_BASE_SHA' .claude/agents/sdlc-lite-author.md`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite "$d/p" && perl -pi -e 's/SDLC_BASE_SHA/X/g' "$d/p/agents/planner.md" && python3 "$d/p/scripts/check.py" "$d/p" 2>&1 | grep 'agents/planner.md' | grep -q SDLC_BASE_SHA`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
