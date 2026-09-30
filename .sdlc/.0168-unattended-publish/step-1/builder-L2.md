<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/fix/SKILL.md: step 5 now has an Unattended rule after the interactive rule. When no person is present (headless, or an unattended goal), it never calls AskUserQuestion and never pushes or opens a pull request; a local commit is the most it may do. It ends with a report listing the work waiting to be published. The interactive rule is unchanged.
- plugins/sdlc-lite/scripts/check.py: new check `fix_unattended_bad`. It fails when the `5. ` line of skills/fix/SKILL.md lacks "Unattended" or "never push". Its built-in negative control removes "never push" and confirms the check flags it.

## Checks
- `grep -E '^5\. ' ... | grep -q 'Unattended'`: pass
- `grep -E '^5\. ' ... | grep -q 'never push'`: pass
- `python3 plugins/sdlc-lite/scripts/check.py`: pass, "ok: 18 role levels, 8 agents checked", rc=0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass, "Codex agent definitions verified", rc=0
- Old-text control: I stashed the SKILL.md edit and ran check.py. It failed with "FAIL skills/fix/SKILL.md: step 5 lacks the Unattended rule with "never push"", rc=1. I then restored the edit.

## Notes
No regeneration was needed because the generated agents were already up to date. The working tree has unrelated changes under .sdlc/0162-* and .sdlc/0168-unattended-publish/handoff.md; I did not touch them.
