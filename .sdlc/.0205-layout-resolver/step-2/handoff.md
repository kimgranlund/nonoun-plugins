## Task goal
Add the `layout` config key and one resolver for ticket dir, roadmap path, and notes path, plus stray checks and onboard variants.

## Step 2: onboard topics variant, then gates green
level: L2
guard timeout: 1300
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Edits in `plugins/sdlc-lite/scripts/onboard.py` (line numbers at HEAD 264be0cb):

1. `Model` (line 478) gains a trailing field `roadmap` whose default is `'.sdlc/roadmap.md'`. Extend the namedtuple `defaults` so every existing `Model(...)` call and selftest fixture keeps working.
2. `build_model` (lines 622-648) sets `roadmap` to `tickets.layout_paths(pathlib.Path(root, '.sdlc')).roadmap` made relative to `root`, in posix form: `.sdlc/roadmap.md` for a flat repo, `.sdlc/tickets/roadmap.md` for topics.
   - `tickets` is imported locally inside the helper body, as tickets.py:929 does for `messages`. tickets.py imports onboard at module level (tickets.py:189), so a top-level import back would be circular.
   - A `tickets.Fail` from a bad `.sdlc/config` is re-raised as `SetupError(str(e))`. `_plan_or_report` (lines 931-938) then prints `onboard.py: <reason>` to stderr, and `setup` and `check` exit 1 with nothing written.
3. `render_templates` (line 530) replaces the literal `.sdlc/roadmap.md` in the root block with `model.roadmap`. For a flat repo the replacement is the identity, so the block text, its digest, and `TEMPLATE_VERSION = 1` (line 307) stay unchanged and every existing block stays `current`. A bump would mark every block stale (design.md:169).
4. Selftest. Add gate `layout-variant` to `GATES` (line 1563), after `lane-text`.
   - Positive, flat: in a `_fixture` with no `.sdlc`, `run_setup` writes a root block whose text equals the unsubstituted template block (`_split_template(ROOT_AGENTS_TEMPLATE).block` with `<N>` set to the version), and `run_check` labels `AGENTS.md` current.
   - Positive, topics: in a fixture whose `.sdlc/config` holds `ticket_root: tickets` and `layout: topics`, the written block names `.sdlc/tickets/roadmap.md` and not `.sdlc/roadmap.md`, its version is `TEMPLATE_VERSION`, and `run_check` labels it current.
   - Negative variants, each of which must be rejected: `('renders the topics text for a flat repo', REAL._replace(render=_render_topics_always))` and `('renders the flat text for a topics repo', REAL._replace(render=_render_flat_always))`.
   - The existing `_selftest` loop prints `gate layout-variant: positive ok, negative ok`.
5. The module docstring says that the root block names the resolved roadmap path. Its "Standard library only" sentence (line 8) also says that the layout is read through a function-local import of the sibling `tickets.py`.

Then run every gate below and fix any red that step 1 or this step introduced, inside the four owning files (`tickets.py`, `onboard.py`, `check.py`, `messages.py`). `check.sh` runs the selftests of every script that imports `tickets` (board, budget, fanout, steps, solo_run, traces), so an exact-output dependent that the grep missed shows up here. A gate already red at the build-start HEAD comes back as Status `inherited red`. At plan time all four were green: `check.sh` rc 0 in 431 s, `check-packaging.py`, `codex_roles.py generate --check`, and `tickets.py --root .sdlc check` rc 0. `onboard.py check` is rc 1 on this repo before any change (missing `docs/layout.md` and topic entries), so it is not a gate.

Depends on: step 1.
### Acceptance criteria
- `d=$(mktemp -d) && s="$PWD/plugins/sdlc-lite/scripts/onboard.py" && git -C "$d" init -q && mkdir "$d/.sdlc" && printf 'ticket_root: tickets\nlayout: topics\n' > "$d/.sdlc/config" && (cd "$d" && python3 "$s" setup >/dev/null 2>&1) && grep -qF '.sdlc/tickets/roadmap.md' "$d/AGENTS.md" && ! grep -qF '.sdlc/roadmap.md' "$d/AGENTS.md" && (cd "$d" && python3 "$s" check 2>/dev/null) | grep -qx 'current AGENTS.md'`
- `d=$(mktemp -d) && e=$(mktemp -d) && s="$PWD/plugins/sdlc-lite/scripts/onboard.py" && git -C "$d" init -q && mkdir "$d/.sdlc" && printf 'ticket_root: tickets\nlayout: nested\n' > "$d/.sdlc/config" && (cd "$d" && ! python3 "$s" setup 2>"$e/err" >/dev/null) && grep -qF 'layout: nested' "$e/err" && test ! -e "$d/AGENTS.md"`
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest | grep -qx 'gate layout-variant: positive ok, negative ok'`
- (guard) `d=$(mktemp -d) && s="$PWD/plugins/sdlc-lite/scripts/onboard.py" && git archive "$SDLC_BASE_SHA" plugins/sdlc-lite/scripts/onboard.py | tar -x -C "$d" && for c in none nested; do r="$d/$c" && mkdir "$r" && git -C "$r" init -q && if [ $c = nested ]; then mkdir "$r/.sdlc" && printf 'ticket_root: tickets\n' > "$r/.sdlc/config"; fi && (cd "$r" && python3 "$d/plugins/sdlc-lite/scripts/onboard.py" setup >/dev/null 2>&1) && (cd "$r" && python3 "$s" check 2>/dev/null) | grep -qx 'current AGENTS.md' || exit 1; done`
- (guard) `grep -qx 'TEMPLATE_VERSION = 1' plugins/sdlc-lite/scripts/onboard.py`
- (guard) `python3 plugins/sdlc-lite/scripts/onboard.py selftest`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxE 'plugins/sdlc-lite/scripts/(tickets|onboard|check|messages)\.py')"`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
