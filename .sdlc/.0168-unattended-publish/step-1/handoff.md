## Task goal
Unattended runs stop at publish and report: they never push or open a pull request, and they list what is waiting in the final report.

## Step 1: /fix stops at publish when no person is present
level: L2

### Do
In `plugins/sdlc-lite/skills/fix/SKILL.md` step 5, add the unattended rule, matching the wording and meaning of `/chain` section 7's Unattended bullet: when no person is present (headless, or an unattended goal), never call AskUserQuestion, never push or open a pull request (a local commit is the most it may do), and end with a report that lists the work waiting to be published. Keep the existing interactive rule unchanged.

Add a contract check to `plugins/sdlc-lite/scripts/check.py` that fails when `skills/fix/SKILL.md` step 5 lacks the phrase "Unattended" together with "never push", in the style of the existing checks, with a built-in negative control. Confirm it fails on the old text and passes on the new one. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` if the check reports generated agents out of date.

### Acceptance criteria
- `grep -E '^5\. ' plugins/sdlc-lite/skills/fix/SKILL.md | grep -q 'Unattended'`
- `grep -E '^5\. ' plugins/sdlc-lite/skills/fix/SKILL.md | grep -q 'never push'`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
