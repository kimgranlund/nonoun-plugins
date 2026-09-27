## Task goal
A step's scope criteria compare against the tree the build started from, and that works whether or not anything gets committed later.

## Step 2: steps.py sets SDLC_BASE_SHA for guard and swap spans
level: L2
### Do
In `plugins/sdlc-lite/scripts/steps.py`, run every span with `SDLC_BASE_SHA` set in its env, so a criterion that names it runs the same under `split --only` and `swap` as under a builder or verifier. Always set the value, never inherit it from the caller's env.
- In `run_guards`/`run_guard`, for `split --only`: set it to `git rev-parse HEAD` at the git toplevel. No build has started, so HEAD is the base.
- In `swap`: set it to the first line of `<step dir>/base-sha` when that is a valid commit, else HEAD.
- Outside git, leave it unset.

Update the module docstring and help text. Add selftest cases:
- `split --only` passes a guard `test "$SDLC_BASE_SHA" = "$(git rev-parse HEAD)"`;
- a `swap` new span sees the stored `base-sha` value;
- `lint` does not flag a criterion `git diff --name-only "$SDLC_BASE_SHA"` as pinning a sha. `pins_sha` already allows it; the case pins that.

Run criteria from the git toplevel.
### Acceptance criteria
- `sp=$PWD/plugins/sdlc-lite/scripts/steps.py && d=$(mktemp -d) && git -C "$d" init -q && git -C "$d" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -q --allow-empty -m i && mkdir "$d/t" && printf '## Goal\ng\n' >"$d/t/handoff.md" && printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- (guard) \140test "$SDLC_BASE_SHA" = "$(git rev-parse HEAD)"\140\n\n## Risks\nNone\n' >"$d/t/planner-L2.md" && python3 "$sp" split --only 1 "$d/t" && test -f "$d/t/step-1/handoff.md"`
- `grep -q SDLC_BASE_SHA plugins/sdlc-lite/scripts/steps.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
