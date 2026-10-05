## Goal
Independently verify the wave-b diff: `git diff 27875a3..HEAD` in this worktree.

## Acceptance criteria
1. docs/lean-sdlc/solo-lane-contract.md and solo-lane-assessment.md: every claim in the assessment matches the cited files and records; digests are plausible; no overclaiming (not-assessed items stay marked); contract follows plugins/progressive-context/skills/progressive-context/references/contracts.md and evidence.md.
2. docs/generative-constructs/01 to 06 carry the shipped-status banner and README.md has a vocabulary table whose mapping agrees with the shipped skill's terms; links resolve.
3. fanout.py: solo_model_label prints the real model per backend (claude and codex, from adapters/codex/models.json); gate_vacuous plus the merge_gate_close change refuses a gate that ran 0 tests unless --allow-empty-gate. Run `python3 plugins/sdlc-lite/scripts/fanout.py selftest`, and show a negative control: temporarily break gate_vacuous (in a throwaway copy or reverted after) and see case 19 fail.
4. No em dashes in the changed files; no files added or edited under docs/reports/.

## Constraints
Read-only except throwaway experiments you revert. No push or publish.
