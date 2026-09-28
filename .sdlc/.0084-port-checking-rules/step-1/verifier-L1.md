<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Dry run of `scripts/run.sh verifier L1` loads both skills: pass. Evidence: the append-system-prompt file it names contains `# Skill: checks-that-bite ` and `# Skill: checking-rules `, and the check exited 0. At HEAD the skill file does not exist, so `verifier.md` could not have listed it and the check would go red.
- `name: checking-rules` frontmatter line: pass. Evidence: the grep exited 0.
- No harness, write-handoff, dispatch-ticket, make-skill, file-bug, check-all, skill_lint, docs_check or reviewer/auditor mentions: pass. Evidence: `test -f` plus the negated grep exited 0. I read the full file and found none of those terms.
- No em dashes: pass. Evidence: `test -f` plus the negated grep for `—` exited 0.
- No bold inline labels: pass. Evidence: the negated grep for `\*\*[^*]+[.:]\*\*` exited 0. The file text shows plain "1. Evidentiary symmetry:" style.
- Required phrases and sections present: pass. Evidence: the greps for steelman, evidentiary symmetry, runtime over claim, `## Output contract`, `## Failure branches` and `## Example` all matched.
- "invariant's unit" and "soft size budget" absent: pass. Evidence: the negated grep exited 0.
- `verifier.md` lists `  - checking-rules` under `skills:` and mentions it at least twice: pass. Evidence: both greps exited 0. The diff shows the skills-list line and the added sentence in the "A criterion with no evidence fails." paragraph.
- `CLAUDE.md` names both skills for the verifier: pass. Evidence: the grep for `verifier ← .*checks-that-bite.*checking-rules` exited 0. The diff shows the intended wording.
- `plugin.json` version is 0.8.4: pass. Evidence: the grep exited 0. The diff shows 0.8.3 to 0.8.4.
- (guard) `verifier.md` still has exactly the four output headings: pass. Evidence: the `## ` headings joined to `## Verdict|## Criteria|## Out of scope changes|## For the next attempt|`, matching exactly.
- (guard) `run.sh`, `level-rubric`, `checks-that-bite` and `sdlc-lite-author.md` are unchanged: pass. Evidence: `git diff --quiet HEAD -- ...` exited 0.
- (guard) `scripts/check.sh` exits 0: pass. Evidence: `rc=0` on a fresh run. The output ends with the ok lines for shellcheck and plugin validate. The six "fail" lines in it are selftest "fails and writes nothing" ok-lines, not failures.
- SKILL.md reads as a verifier's discipline for checking a builder's step, with no leftover harness-flow context: pass. Evidence: I read the whole file. The intro, the three procedure rules, the output contract, the failure branches and the examples all speak of verifier, builder, `builder-*.md` and acceptance criteria. It says it complements `checks-that-bite`. No harness flow context remains.

## Out of scope changes
None. `git status` shows these changes, all within the step:
- New: `skills/checking-rules/`.
- Modified: `agents/verifier.md`, `CLAUDE.md` and `plugin.json`.
- Task-side files: `.sdlc/0084-port-checking-rules/handoff.md`, `planner-L2.md`, `runs.jsonl` and the `step-1/` artifacts.

The `.sdlc` task files are the task's own artifacts. `git diff HEAD` lists no other tracked files, and `.claude/` is clean.

## For the next attempt
None
