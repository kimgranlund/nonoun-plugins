## Task goal
Re-verify branch t0185 after the one-token fix the L3 branch verifier asked for (`docs/maintenance/sdlc-internals.md` refers to the evals guard as `check.py` docstring item 15).

## Step 1: Re-verify the fix
level: L1

### Do
Read-only. Confirm the single failing item of `.sdlc/verify-t0185/step-1/verifier-L3.md` is fixed and nothing else broke.

### Acceptance criteria
- `grep -q 'docstring item 15 runs the check' docs/maintenance/sdlc-internals.md`
- `! grep -q 'docstring item 14 runs the check' docs/maintenance/sdlc-internals.md`
- `grep -q '^15. Evals lock' plugins/sdlc-lite/scripts/check.py`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
