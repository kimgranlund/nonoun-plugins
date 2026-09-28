<!-- role=filer level=L1 model=sonnet effort=medium -->
Both steps built and verified pass, check.sh green. No warnings, no follow-ups noted in artifacts.

## Warnings
None

## PR title
T-0110: Exempt the deliberate ancestry check from the pinned-sha lint

## PR body
Summary: `steps.py`'s pinned-sha lint (`pins_sha`) now exempts exactly the deliberate ancestry form `git merge-base --is-ancestor <sha> HEAD`; every other pinned commit sha (`git diff <sha>`, `<sha>..HEAD`, `<sha>^`, a span holding the ancestry form plus a second pinned sha, or the ancestry form naming a different ref or with the sha and `HEAD` swapped) is still refused as a plan defect.

Changes:
- `plugins/sdlc-lite/scripts/steps.py`: added `ANCESTRY_RE`; `pins_sha` strips the exempt ancestry span before running the existing sha test. Updated the `split` and `lint` docstring paragraphs and the lint hint to name the exemption. Added two `(k3)` selftest cases (ancestry-form pass, ancestry-plus-second-sha refuse), with fixture shas built by concatenation so no literal sha lands in source.
- `plugins/sdlc-lite/agents/planner.md` rule 6: names the ancestry exemption as the one allowed pinned-sha form.
- `CLAUDE.md` (repo root), `scripts/steps.py` bullet: extended the pinned-sha parenthetical with the same exemption wording.
- `.claude/agents/sdlc-lite-author.md`: plan-defect route line notes the exemption.

Verification:
- Step 1 (builder L2 / verifier L1, sonnet medium): verifier confirmed each criterion red-then-green against a pre-build worktree at `$SDLC_BASE_SHA`, including that the ancestry form alone is no longer pinned, that all other pinned-sha forms (including ancestry-plus-second-sha) stay refused, that the docstring names `is-ancestor`, that both new selftest cases print with `pass`/`refuse` labels, and that `steps.py selftest` ends `PASS`. Read the full diff against base to confirm the `||`, fixed-set-count, clean-status, and `bash -n` checks were untouched.
- Step 2 (builder L1 / verifier L1 opus medium): verifier confirmed each doc grep red-then-green against the pre-build worktree, confirmed identical exemption wording across all three docs, and confirmed `plugins/sdlc-lite/scripts/check.sh` passes on the built tree while a mutated base copy (Haiku swapped into a level table) makes it fail, proving the gate bites. No out-of-scope changes found in either step.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
`steps.py`'s pinned-sha lint now allows the deliberate ancestry check `git merge-base --is-ancestor <sha> HEAD`; every other pinned commit sha is still refused as a plan defect.

## Follow-ups
None
