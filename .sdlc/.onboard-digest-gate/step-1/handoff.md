## Task goal
The onboard selftest fails when the marker hash is computed wrongly.

## Step 1: Add a digest gate to the onboard selftest
level: L2

### Do
In `plugins/sdlc-lite/scripts/onboard.py`, add a selftest gate named `digest`, built like the existing gates. Positive case: the real hash function returns, for fixed block texts, the expected values written as literals in the gate (compute them once with `printf ... | shasum -a 256` and state the command in a comment). Cover one LF text and the same text with CRLF endings, which must give the same value. Negative control: a variant that hashes without normalizing line endings, and a variant that returns a different prefix length, must each be rejected. Confirm that temporarily breaking the real function makes the gate print FAIL, then restore it.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest | grep -qxF "gate digest: positive ok, negative ok"`
- (guard) `python3 plugins/sdlc-lite/scripts/onboard.py selftest`
