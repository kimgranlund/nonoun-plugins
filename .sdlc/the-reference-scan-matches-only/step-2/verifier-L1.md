<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF "relative to the citing file" CLAUDE.md`: pass. Evidence: exits 0 in the tree. `git show HEAD:CLAUDE.md | grep -qF ...` exits 1, so the check bites. The added text is at the `scripts/tickets.py` Layout entry: "The scan finds the folder name, then keeps files with a literal `<rel>/<slug>` or a path token that resolves to the folder, whether toplevel-relative, relative to the citing file's directory, or absolute. Only matched tokens are rewritten, keeping their form; there is no case folding, symlink resolution, `~` expansion or self-reference handling."
- `grep -qF "relative to the citing file" plugins/sdlc-lite/scripts/tickets.py`: pass. Evidence: exits 0 in the tree and 1 at HEAD. The diff adds the rule and its limits to the `close` help paragraph (line ~25) and adds "also matching paths relative to the citing file, with the same limits" to the `archive` paragraph (line ~56).
- `grep -qF "relative to the citing file" .claude/agents/sdlc-lite-author.md`: pass. Evidence: exits 0 in the tree and 1 at HEAD. The diff adds "(the scan also resolves paths relative to the citing file and absolute paths, and rewrites only matched tokens, keeping their form)".
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: pass. Evidence: prints `tickets selftest: PASS`. This is a gate: it held green, and this step's diff for tickets.py is help text only.
- (guard) `plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exits 0. The full output was captured and ends with `run selftest: PASS`, `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.
- Em dash count on added lines prints 0: pass. Evidence: the command prints `0`. To confirm it can go red, the same pipeline run on `printf '+a — b\n'` prints `1`.

## Out of scope changes
- `plugins/sdlc-lite/scripts/tickets.py` has code changes in `outside_refs`, `ref_tokens` and the rewrite logic, plus docstrings. I read the diff: these are step 1's work, which has its own `step-1/verifier-L2.md`, and they are not part of this step. Not attributed to step 2.
- `.sdlc/the-reference-scan-matches-only/handoff.md` (Goal, Intent and Constraints filled in) and the untracked `planner-L2.md`, `runs.jsonl`, `step-1/` and `step-2/` are planning and run artifacts, which I checked with `git diff` on the handoff. Not project scope creep.
- `plugins/sdlc-lite/skills/ticket/SKILL.md` has a one-line change. The step allows it "only if it describes the scan", and the replaced text did describe it ("...it;" became the scan rule sentence, per the word diff). In scope.

A minor leftover that does not fail any criterion: the `close` help still says "close --rewrite-refs rewrites <rel>/<slug> to <rel>/.<slug>", and the `archive` help says "rewrites each cite to <rel>/.NNNN-<slug>". Both are slightly less exact than the new "keeping their form" sentence. I considered filing this as a fail, but the builder would rightly answer that the limits sentence right before it gives the precise rule, and no criterion or Do item requires rewording that line. I dropped it.

## For the next attempt
None
