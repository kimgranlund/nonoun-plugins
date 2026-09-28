## Task goal
The verifier applies review discipline: evidence to dismiss, run rather than trust a claim, steelman before filing.

## Step 1: Add the checking-rules skill, wire it into the verifier, update the records
level: L2
### Do
All paths below are relative to `plugins/sdlc-lite/` unless they start with `../../` (the repo root).

1. Create `skills/checking-rules/SKILL.md`. It is a trimmed port of `~/.claude/plugins/cache/nonoun-plugins/harness/3.19.6/skills/checking-rules/SKILL.md`.
   - Frontmatter keeps `name: checking-rules`, `disable-model-invocation: false` and `user-invocable: true`.
   - Rewrite the `description` for a reviewer or verifier checking a builder's step. Drop its NOT clauses, because they name harness skills.
   - Keep the intro, `## Procedure` (three rules: evidentiary symmetry, runtime over claim, steelman before filing), `## Output contract`, `## Failure branches` with its "Done when" paragraph, and `## Example`.
   - Reword all of it for a verifier checking a builder's step against acceptance criteria. For example, the builder's `builder-*.md` summary is the claim under review, and a dismissed criterion or out-of-scope concern needs a cited check.
   - Drop "The invariant's unit" and "Semantic-diff soft size budget" entirely.
   - The file must not mention harness, write-handoff, dispatch-ticket, make-skill, file-bug, check-all-*, skill_lint, docs_check, or reviewer/auditor.
   - Repo style: no em dashes, and no bold inline labels. For example, `1. **Evidentiary symmetry.**` becomes a plain `1. Evidentiary symmetry:` or a sub-heading.
   - Say that it complements the `checks-that-bite` skill, which a verifier also loads.
2. `agents/verifier.md`:
   - Add `  - checking-rules` under `skills:` after `  - checks-that-bite`.
   - In the paragraph that starts "A criterion with no evidence fails.", add one sentence. It names the checking-rules skill: a dismissal or an accepted builder claim cites the check behind it, and each fail reason is steelmanned before it is filed.
   - Change no other rule and none of the four output sections.
3. `../../CLAUDE.md`, Layout, the "Agent skills" bullet: change `verifier ← \`checks-that-bite\` (brought in from the user-level skill)` so it names both skills, e.g. `verifier ← \`checks-that-bite\` (brought in from the user-level skill) and \`checking-rules\` (ported from harness checking-rules, trimmed)`.
   - `../../.claude/agents/sdlc-lite-author.md` has no line listing the verifier's skills. Line 24 cites checks-that-bite as author discipline. Leave that file unchanged.
4. `.claude-plugin/plugin.json`: change `"version"` from `0.8.3` to `0.8.4`.
5. Leave `scripts/run.sh`, `skills/level-rubric/`, and `skills/checks-that-bite/` unchanged. Do not commit.

### Acceptance criteria
Run every command from `plugins/sdlc-lite/`.
- `f=$(SDLC_DRY_RUN=1 scripts/run.sh verifier L1 ../../.sdlc/0084-port-checking-rules/handoff.md | grep -oE 'append-system-prompt-file [^ ]+' | cut -d' ' -f2); grep -q '^# Skill: checks-that-bite ' "$f" && grep -q '^# Skill: checking-rules ' "$f"`
- `grep -q '^name: checking-rules$' skills/checking-rules/SKILL.md`
- `test -f skills/checking-rules/SKILL.md && ! grep -qiE 'harness|write-handoff|dispatch-ticket|make-skill|file-bug|check-all|skill_lint|docs_check|reviewer/auditor' skills/checking-rules/SKILL.md`
- `test -f skills/checking-rules/SKILL.md && ! grep -q '—' skills/checking-rules/SKILL.md`
- `test -f skills/checking-rules/SKILL.md && ! grep -qE '\*\*[^*]+[.:]\*\*' skills/checking-rules/SKILL.md`
- `grep -qiE 'steelman' skills/checking-rules/SKILL.md && grep -qiE 'evidentiary symmetry' skills/checking-rules/SKILL.md && grep -qiE 'runtime over claim' skills/checking-rules/SKILL.md && grep -qiE '^## Output contract' skills/checking-rules/SKILL.md && grep -qiE '^## Failure branches' skills/checking-rules/SKILL.md && grep -qiE '^## Example' skills/checking-rules/SKILL.md`
- `! grep -qiE "invariant's unit|soft size budget" skills/checking-rules/SKILL.md && test -f skills/checking-rules/SKILL.md`
- `grep -qE '^  - checking-rules$' agents/verifier.md && test "$(grep -c 'checking-rules' agents/verifier.md)" -ge 2`
- `grep -qE 'verifier ← .*checks-that-bite.*checking-rules' ../../CLAUDE.md`
- `grep -q '"version": "0.8.4"' .claude-plugin/plugin.json`
- (guard) `test "$(grep '^## ' agents/verifier.md | tr '\n' '|')" = '## Verdict|## Criteria|## Out of scope changes|## For the next attempt|'`
- (guard) `git diff --quiet HEAD -- scripts/run.sh skills/level-rubric skills/checks-that-bite ../../.claude/agents/sdlc-lite-author.md`
- (guard) `scripts/check.sh` exits 0. It exits 0 on the current tree, so any failure is new.
- The new SKILL.md reads as a verifier's discipline for checking a builder's step, with no leftover harness-flow context. A reviewer checks this by reading it.
