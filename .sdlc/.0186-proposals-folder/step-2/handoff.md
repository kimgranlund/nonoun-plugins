## Task goal
Repeated failures in past runs become evidence-backed candidate proposals in a folder, and nothing is applied without an eval.

## Step 2: Add the .sdlc/proposals entry files, the router line, the docs, and the live run
level: L2
### Read first
- `.sdlc/AGENTS.md`
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1. Run from the repository root and use no em dashes. Each fact has one authoritative place: the format, the patterns, and the transitions live in `.sdlc/proposals/AGENTS.md` and in the proposals.py docstring. The other docs link there instead of copying them.

1. Write `.sdlc/proposals/CLAUDE.md` as exactly `@AGENTS.md` and a newline.
2. Write `.sdlc/proposals/AGENTS.md`. It must be self-contained, so a role that reads only this file can scan, list, show, accept, reject, and promote (handoff Common rules: no skill is added). Its sections, in order:
   - `# Proposals`, then one paragraph:
     - The folder holds candidate changes that `proposals.py scan` mines from past runs (`runs.jsonl`, builder and verifier results, `notes.md`).
     - Nothing is applied automatically. `accept` needs a valid eval in `.sdlc/evals/`, and `promote` only files an idea ticket through `tickets.py new idea`.
     - It never edits a plugin file, runs an experiment, or changes a model default.
     - Run every command from the repository root.
   - `## File format`: the `<kind>-<8 hex>/proposal.md` folder rule, each front matter field in order with its meaning (`P-NNNN` ids), the stamps, the `## Evidence` line shape, the `## Proposed change` line, and one example file.
   - `## Patterns`: the six kinds (`verifier-fail`, `replan`, `builder-bump`, `next-attempt`, `plan-defect`, `follow-up`), each with its source, subject, occurrence, and quote, as in step 1. Also the two-occurrence threshold, the closed-ticket dot rule, and the skipped folders.
   - `## Statuses`: `candidate`, `accepted`, `rejected`, `promoted`; the three allowed moves and the stamps each writes. No move goes backward.
   - `## Procedures`:
     - Scan: `python3 plugins/sdlc-lite/scripts/proposals.py scan`, and `--proposals <dir>` for a look that writes elsewhere.
     - List: `proposals.py list`.
     - Show: `proposals.py show <id>`.
     - Accept: `proposals.py accept <id> --eval .sdlc/evals/<file>`, after adding the eval through `.sdlc/evals/AGENTS.md`.
     - Reject: `proposals.py reject <id> --reason TEXT`.
     - Promote: `proposals.py promote <id>`.
     - Never edit a proposal's front matter by hand.
   - `## Limits`:
     - Quotes collapse whitespace, write an em dash as a hyphen, and are cut at 160 characters.
     - `next-attempt` reads verifier results only. Follow-ups come from `notes.md` only, and `fix-now:` items rarely reach it, because they are finished before close.
     - Ids are not unique across parallel worktrees: scan refuses a duplicate id until it is renumbered.
     - A folder moved other than by the close rename starts a new pattern. scan never deletes a proposal.
     - A proposal citing an open ticket folder makes `tickets.py close` refuse (its `git grep` reference check) until `--rewrite-refs` or `--force`.
3. In `.sdlc/AGENTS.md`, add this line to the `## Other records` list after the Evals line, outside the generated block, without editing inside the block:

   ```
   - Proposals: `proposals/` holds candidate changes that `proposals.py scan` mined from past runs; read `proposals/AGENTS.md` before scanning, accepting, rejecting, or promoting one.
   ```

   `tickets.py` keeps every byte outside the managed markers (tickets.py docstring; T-0185 placed the Evals line there and verified `tickets.py check` stayed ok).
4. In `docs/maintenance/sdlc-internals.md`, add an entry headed exactly ``## `scripts/proposals.py` `` after the `scripts/evals.py` entry. It covers:
   - the purpose
   - the CLI with `--root`, `--proposals`, and `--plugin`, the six commands, and the exit codes
   - its reads (evals.py `validate_eval` in accept, tickets.py `new idea` in promote)
   - the six rule markers and the selftest's negative controls
   - a link `../../.sdlc/proposals/AGENTS.md` for the format and the patterns
5. In `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, add this line to the layout block after the `.sdlc/evals/` line, aligned like its neighbours. handoff-format is not a preloaded skill (agents preload only level-rubric, decompose, checks-that-bite, and checking-rules), so the Codex TOML does not change.

   ```
   .sdlc/proposals/        candidate changes mined from past runs (<kind>-<hash>/proposal.md, P-NNNN), written by scripts/proposals.py scan; accept needs an eval in .sdlc/evals/, promote files an idea ticket; its AGENTS.md documents the format
   ```

6. In `plugins/sdlc-lite/AGENTS.md`, add to the Verification list after the evals line: ``- Proposals mined from runs: `python3 plugins/sdlc-lite/scripts/proposals.py selftest`; read [the proposals entry file](../../.sdlc/proposals/AGENTS.md) before scan, accept, reject, or promote.``
7. Run the live proof and record it in `docs/validation/proposals-live-run.md`, in the shape of `docs/validation/evals-live-run.md`. No model call is needed.
   - Setup, from the repository root:

     ```
     R=$(pwd)
     T=$(mktemp -d)
     P=plugins/sdlc-lite/scripts/proposals.py
     src() { find .sdlc \( -name runs.jsonl -o -name notes.md -o -name '*-L[1-5]*.md' \) -type f ! -path '.sdlc/proposals/*' ! -path '.sdlc/messages/*' -print0 | sort -z | xargs -0 shasum -a 256; }
     plg() { find plugins -type f -print0 | sort -z | xargs -0 shasum -a 256; }
     ```

   - The source manifest covers only what scan reads, less the git-ignored mailbox that other sessions write. run.sh writes this step's `.log` and `.running` files during the build, so a whole-`.sdlc` hash would differ for reasons unrelated to scan.
   - Run the arms after items 1 to 6 are done, and change no file between arm 1 and arm 6.
   - Record each arm's exact command, exit code, and output:
     1. Before: `src >"$T/src.before"`, `plg >"$T/plg.before"`, `ls -A .sdlc/proposals`.
     2. Scan this repository's own `.sdlc/` read-only, writing the candidates to the temp dir: `python3 "$P" --root .sdlc --proposals "$T/proposals" scan` gives exit 0.
     3. Candidates and evidence: `python3 "$P" --root .sdlc --proposals "$T/proposals" list`, then `show` for every id. Paste the list and every proposal's text. A rehearsal with a prototype found 18 `replan` candidates and one `plan-defect` with 12 evidence lines; record what the real script finds.
     4. Idempotence: hash `$T/proposals` (`find "$T/proposals" -type f -exec shasum -a 256 {} + | sort`), scan again, hash again, and `cmp` the two (exit 0). The output ends `0 new, 0 updated, <n> unchanged`.
     5. Negative controls on the transitions (writing only under `$T`):
        - `python3 "$P" --root .sdlc --proposals "$T/proposals" accept P-0001` gives exit 1 with `no eval given`.
        - `accept P-0001 --eval docs/validation/evals-live-run.md` gives exit 1 with `is not in`.
        - `cmp` shows P-0001's file unchanged.
        - Do not run `promote` against the real `.sdlc`: it would file a real ticket.
     6. Sources and plugins unchanged: `src >"$T/src.after"`, `plg >"$T/plg.after"`, and both `cmp` give exit 0. `ls -A .sdlc/proposals` still lists only `AGENTS.md` and `CLAUDE.md` (and `.DS_Store` if Finder wrote one).
     7. Negative control on the read-only check:
        - `mkdir "$T/copy" && cp -R .sdlc "$T/copy/.sdlc"`.
        - Write `$T/mutant/proposals.py` with the `# rule: read-only` line replaced the way step 1's read-only negative control replaces it.
        - Hash the copy's sources with `(cd "$T/copy" && src)`, run `python3 "$T/mutant/proposals.py" --root "$T/copy/.sdlc" --proposals "$T/copy-proposals" --plugin "$R/plugins/sdlc-lite" scan`, and hash again.
        - `cmp` gives exit 1. Record how many source lines differ. This shows that the before and after manifest catches a scan that writes a source.
     8. Cleanup: `rm -rf "$T"`. If it is denied, record that.
   - The candidates go to a temp dir, not to `.sdlc/proposals/`, for two reasons. `tickets.py close` refuses while any file cites an open ticket folder (tickets.py docstring, close: `git grep --untracked -lF <rel>/<slug>`), so committed candidates citing `.sdlc/0183-...` or this ticket's own folder would block those closes. And untriaged candidates should not be committed by a build.
   - An arm that cannot run is recorded as unverified, never replaced by a fixture.
   - The doc's sections hold the exact strings the criteria grep for:
     - `## Environment`: the date (`2026-..-..`), the OS, `python3 --version`, the commit (`git rev-parse --short HEAD`), and a note that the tree includes this ticket's uncommitted changes.
     - `## Commands`: the exact commands, including `proposals.py --root .sdlc --proposals`.
     - `## Evidence`: per arm, the exit code written as `exit 0` or `exit 1`, the list, every proposal (so `pattern: replan .sdlc/` and `pattern: plan-defect` appear), the `0 new, 0 updated` line, `no eval given`, `is not in`, arms 5 and 7 each labeled with the lowercase words `negative control`, and the unchanged `plugins/` manifest.
     - `## Limits`:
       - one machine
       - `promote` ran only in the selftest, and no ticket was filed here
       - the manifest covers the sources and `plugins/`, not logs
       - quotes are cut at 160 characters
       - no candidate was committed

Left untouched on purpose:
- `docs/lean-sdlc/design.md:152`: a design record that already says each planned folder gets its own entry file when built.
- Root `AGENTS.md`: it routes SDLC changes to `plugins/sdlc-lite/AGENTS.md`.
- `skills/level-rubric/SKILL.md`: it is preloaded, so an edit would regenerate the Codex TOML.
### Acceptance criteria
- `test "$(cat .sdlc/proposals/CLAUDE.md)" = '@AGENTS.md'`
- `for s in "## File format" "## Patterns" "## Statuses" "## Procedures" "## Limits" "proposals.py scan" "proposals.py list" "proposals.py show" "proposals.py accept" "proposals.py reject" "proposals.py promote" "--proposals" "P-NNNN" "candidate" "accepted" "rejected" "promoted" "verifier-fail" "replan" "builder-bump" "next-attempt" "plan-defect" "follow-up" "## Evidence" "## Proposed change" ".sdlc/evals/" "tickets.py new idea" "--rewrite-refs"; do grep -qF -- "$s" .sdlc/proposals/AGENTS.md || exit 1; done`
- `awk '/sdlc-lite:managed:end/{e=1; next} e && /proposals\/AGENTS\.md/{f=1} END{exit !f}' .sdlc/AGENTS.md`
- ``grep -qxF '## `scripts/proposals.py`' docs/maintenance/sdlc-internals.md && grep -qF '.sdlc/proposals/' plugins/sdlc-lite/skills/handoff-format/SKILL.md && grep -qF 'scripts/proposals.py' plugins/sdlc-lite/AGENTS.md``
- `f=docs/validation/proposals-live-run.md && for s in "## Environment" "## Commands" "## Evidence" "## Limits" "proposals.py --root .sdlc --proposals" "no eval given" "is not in" "exit 0" "exit 1" "pattern: replan .sdlc/" "pattern: plan-defect" "P-0001" "0 new, 0 updated" "negative control" "plugins/"; do grep -qF -- "$s" "$f" || exit 1; done`
- `grep -qE "2026-[0-9]{2}-[0-9]{2}" docs/validation/proposals-live-run.md`
- `test -f .sdlc/proposals/AGENTS.md && test -f .sdlc/proposals/CLAUDE.md && test -z "$(find .sdlc/proposals -mindepth 1 ! -name AGENTS.md ! -name CLAUDE.md ! -name .DS_Store)"`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/proposals.py -e plugins/sdlc-lite/scripts/check.sh -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e plugins/sdlc-lite/AGENTS.md -e docs/validation/proposals-live-run.md | { ! grep -q .; }`
