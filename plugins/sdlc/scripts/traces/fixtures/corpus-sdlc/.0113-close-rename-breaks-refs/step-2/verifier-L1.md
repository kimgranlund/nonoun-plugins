<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF -- '--rewrite-refs' CLAUDE.md`: pass. Evidence: the grep printed `ok CLAUDE.md`. `git show HEAD:CLAUDE.md | grep -cF -- '--rewrite-refs'` gives 0, so the check goes red at HEAD.
- `grep -qF -- '--rewrite-refs' plugins/sdlc/skills/ticket/SKILL.md`: pass. Evidence: printed `ok`. The HEAD count is 0, so it goes red at HEAD.
- `grep -qF -- '--rewrite-refs' plugins/sdlc/skills/file/SKILL.md`: pass. Evidence: printed `ok`. The HEAD count is 0.
- `grep -qF -- '--rewrite-refs' plugins/sdlc/skills/handoff-format/SKILL.md`: pass. Evidence: printed `ok`. The HEAD count is 0. The diff shows both `.NNNN-<slug>` lines updated.
- `grep -qF -- '--rewrite-refs' .claude/agents/sdlc-lite-author.md`: pass. Evidence: printed `ok`. The HEAD count is 0. The diff adds the refusal, `--rewrite-refs`, `--force` and the /file skill to the dot-prefix sync line.
- `grep -q 'Rewrite references' plugins/sdlc/skills/file/SKILL.md`: pass. Evidence: printed `ok RR`. The diff of step 3.1 lists the options in the required order: "Rewrite references" (recommended), "Leave open", "Close anyway". It says an unattended run stops and never rewrites silently.
- (guard) `bash plugins/sdlc/scripts/check.sh`: pass. Evidence: exit 0. The tail shows run selftest, hook selftest and hook live probe selftest PASS, shellcheck ok, plugin validate ok.
- (guard) only `tickets.py` differs under `scripts/` and `hooks/`: pass. Evidence: the test printed `ok guard2`. `git diff --stat` lists `tickets.py` as the only file under those directories.
- (guard) `tickets.py close --help` mentions `--rewrite-refs`: pass. Evidence: printed `ok guard3`.
- Observable: the `tickets.py` diff holds only step 1's work: pass. Evidence: I read the full diff. The hunks are the docstring and `Usage:` edits, the `outside_refs` helper, the `rewrite_refs` kwarg with its refusal, rewrite and dry-run `rewrite <file>` lines in `cmd_close`, the `(u) refs:` selftest cases, and the `--rewrite-refs` parser flag and `main` kwarg. No other hunk appears.

## Out of scope changes
None. `git diff HEAD --stat` shows only the five doc files the step named plus step 1's `tickets.py`. The untracked `.sdlc/` artifacts are task records, not project files.

## For the next attempt
None
