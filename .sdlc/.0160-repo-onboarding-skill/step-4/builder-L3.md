<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `docs/reports/onboard-live-run.md`: new dated report of the live run gate. It gives the environment, method, prompt, exact commands, the required results table, the answers observed, and limits.
- `docs/repo-onboarding/README.md`: added an Evidence link to `../validation/onboard-live-run.md`.
- `docs/README.md`: added a link to `validation/onboard-live-run.md` after the other onboarding validation entries.

## Checks
- Host versions: `claude --version` gave 2.1.285 and `codex --version` gave codex-cli 0.154.0.
- Setup, run 3 times (one throwaway project per run, `git init` then `python3 .../onboard.py setup`): exit 0 each time. Each run created AGENTS.md, CLAUDE.md, docs/AGENTS.md, docs/CLAUDE.md and docs/layout.md. The root AGENTS.md block contains `Managed by SDLC Lite onboard, template 1.`
- Claude Code, block present (`claude -p "<prompt>" --tools "" --output-format json`): answered `Managed by SDLC Lite onboard, template 1.` Model claude-fable-5-1, 1 turn.
- Claude Code, block deleted (same project, block removed from AGENTS.md with sed, then `grep -rn "Managed by"` found nothing): answered `ABSENT`.
- Codex, block present (`codex exec -s read-only -m gpt-6-astra --json -o <file> "<prompt>" < /dev/null`): answered `Managed by SDLC Lite onboard, template 1.` The event stream had 0 `command_execution` items.
- Codex, block deleted: answered `ABSENT`, with 0 `command_execution` items.
- Acceptance criterion 1 (four table rows): exit 0.
- Acceptance criterion 2 (`gpt-6-astra`): exit 0.
- Acceptance criterion 3 (link in repo-onboarding README): exit 0.
- Acceptance criterion 4 (link in docs README): exit 0.
- `git diff --check`: exit 0. `git diff --no-index --check /dev/null <new report>` printed no whitespace errors. Its exit 1 only means the files differ.

## Notes
- All four arms gave the expected result. An answer counts as reported only if it quotes `, template 1.`, and that text is not in the prompt.
- Some arms ran more than once, and every earlier run gave the same answer as the recorded one:
  - Claude Code ran first with a prompt missing the opening "Do not run any command or read any file." sentence.
  - The first Codex present-arm run left stdin open. The recorded present run was repeated in a fresh project from the same setup. The report's Limits section says this.
- The throwaway projects are in `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/tmp.HxvEeKNiKL`, outside the repo, and hold no transcripts in the repo. My `rm -rf` of that folder was denied by permissions, so it is still there. The OS temp cleaner or the user can remove it.
- No commit was made.
