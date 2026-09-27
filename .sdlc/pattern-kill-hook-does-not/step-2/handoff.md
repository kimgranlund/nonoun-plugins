## Task goal
Inside a role run, `plugins/sdlc-lite/hooks/block-pattern-kill.sh` blocks a kill word assigned to a variable through a command substitution and then expanded as a command (`p=$(command -v pkill); $p x`, `k=$(which killall); ${k} node`, backtick forms too), while `cmd=$(command -v ls); $cmd -la` and quoted mentions still pass.

## Step 2: Gates green
level: L1
### Do
Run `bash plugins/sdlc-lite/scripts/check.sh` from the repo root and fix any red step 1 introduced (a shellcheck warning in the hook or the selftest, a fixture with the wrong expected exit code, a check.py doc guard), touching only the files step 1 changed. A gate already red at the pre-build HEAD is reported as Status `inherited red: <tests>`, not fixed here. Never commit.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
