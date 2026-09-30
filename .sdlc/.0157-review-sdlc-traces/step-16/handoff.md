## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 16: CLI: ingest, detect, clusters
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Extend `traces/cli.py`: `ingest <repo> [--lanes-dir DIR]... [--out DIR] [--bench-dir DIR] [--rerun-criteria] [--load-series PATH]` runs `ingest.run` and prints the events.jsonl path; `detect [--repo REPO] [--out DIR]` reads `<out>/events.jsonl` and `aux.json`, runs the four detector families, writes findings through `findings.write`, prints each note and then the findings.jsonl path; `clusters --max N [--repo REPO] [--out DIR]` prints `findings.clusters(out, N)` as JSON; `detect` and `clusters` resolve the out dir exactly as ingest does (`REPO` defaults to `.`). Stages 1 and 2 spawn no `claude` or `codex` process, so a run under a PATH whose `claude` and `codex` exit 99 still exits 0. Add `.sdlc/runtime/` to the root `.gitignore`. Update the module docstring of `traces.py` with the four subcommands.
### Acceptance criteria
- `d=$(mktemp -d) && python3 plugins/sdlc-lite/scripts/traces.py ingest . --out "$d/out" | grep -q 'events.jsonl' && python3 plugins/sdlc-lite/scripts/traces.py detect --out "$d/out" | grep -q 'findings.jsonl' && python3 plugins/sdlc-lite/scripts/traces.py clusters --max 2 --out "$d/out" > "$d/clusters.txt" && test -s "$d/out/events.jsonl" && test -f "$d/out/aux.json" && test -f "$d/out/cursor.json" && test -f "$d/out/findings.jsonl"`
- `d=$(mktemp -d) && printf '#!/bin/sh\nexit 99\n' > "$d/claude" && cp "$d/claude" "$d/codex" && chmod +x "$d/claude" "$d/codex" && PATH="$d:$PATH" python3 plugins/sdlc-lite/scripts/traces.py ingest . --out "$d/out" && PATH="$d:$PATH" python3 plugins/sdlc-lite/scripts/traces.py detect --out "$d/out"`
- `grep -qxF '.sdlc/runtime/' .gitignore`
- `grep -q 'clusters' plugins/sdlc-lite/scripts/traces.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
