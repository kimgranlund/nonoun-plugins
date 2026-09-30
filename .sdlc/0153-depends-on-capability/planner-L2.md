<!-- role=planner level=L2 model=opus effort=medium -->
Probes done: step 1 and step 2 criteria are red for the right reason, and every guard and gate is green now. Writing the plan.

## Goal
`tickets.py` accepts `file:<path>` and `cap:<name>` entries in `depends:` alongside `T-NNNN`, plus an optional `provides:` list, so a ticket can wait on the specific fix it needs. Check, roadmap ordering and rendering, the selftest, and the docs all cover the new forms.

## Step 1: Parse, validate, order, and render file: and cap: dependencies in tickets.py
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Change only `plugins/sdlc-lite/scripts/tickets.py`.

1. **Entry kinds.** Classify each `depends` entry:
   - A ticket id matches `ID_RE`, unchanged.
   - `file:<path>` needs a non-empty path that does not start with `/` and has no `..` segment.
   - `cap:<name>` needs a name matching `[A-Za-z0-9][A-Za-z0-9._-]*`.
   - Anything else is malformed.
2. **`provides`.** Add an optional front matter key `provides: [<name>, ...]`. Never add it to `REQUIRED`.
3. **`problems()` additions:**
   - A malformed entry gives `<slug>: depends entry '<entry>' is not T-NNNN, file:<path> or cap:<name>`.
   - A well-formed `T-NNNN` with no ticket keeps today's `<slug>: depends on <id>, which no ticket has`.
   - A `cap:<name>` that no ticket (any status) lists in `provides` gives `<slug>: depends on cap:<name>, which no ticket provides`.
   - A `provides` that is not a list gives `<slug>: provides '<value>' is not a list like [name]`.
   - A `provides` item that is not a valid name is an error naming the slug and the item.
   - A `file:` path that does not exist is not an error.
4. **Ordering.** In `order()`, each `cap:` entry adds an edge to every ticket that provides that name, so `cycles()` also detects cycles through capabilities. `file:` entries never add edges. Refactor `deps_of` as needed; keep the Kahn tie-break by id.
5. **Rendering.** In `render()`, the Depends on cell joins entries with `, ` as today:
   - `T-NNNN` entries render unchanged, so a roadmap of T-only tickets stays byte-identical.
   - `file:<path>` renders as is when the path exists, else as `file:<path> (unmet)`. Resolve the path against the git toplevel of the ticket root (`git -C <root> rev-parse --show-toplevel`), falling back to the root's parent directory when git fails or the root is outside git.
   - `cap:<name>` renders as is when some `status: done` ticket provides it, else as `cap:<name> (unmet)`.
   - Escape `|` in entries the same way as titles.
6. **Module docstring.** Document the three entry forms and `provides` (text including `cap:<name>` and `provides`). Note that the roadmap goes stale when a named file appears or a provider closes, so `roadmap` must be rerun.
7. **Selftest.** Add cases whose labels contain these exact strings:
   - `cap: edge orders after its provider`
   - `file: entry that exists does not block`
   - `malformed depends entry fails check`
   - `unprovided cap: fails check`

   Also add a case for a cap cycle and a case for a non-list `provides`. Keep every existing `T-NNNN` fixture and expectation unchanged.
### Acceptance criteria
- `R=$(mktemp -d)/.sdlc; mk(){ mkdir -p "$R/$1"; printf -- '---\nid: %s\ntitle: "x"\ntype: feature\nstatus: %s\nsize: M\npriority: P2\ndepends: [%s]\ncreated: 2026-01-01\n%b---\n' "$2" "$3" "$4" "$5" > "$R/$1/handoff.md"; }; mk alpha T-0001 ready cap:widget ""; mk beta T-0002 done "" "provides: [widget]\n"; python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" roadmap && grep -F "| T-0001 |" "$R/roadmap.md" | grep -qF "| cap:widget |" && awk '/\| T-0002 \|/{b=NR} /\| T-0001 \|/{a=NR} END{exit !(b && a && b<a)}' "$R/roadmap.md"`
- `R=$(mktemp -d)/.sdlc; mk(){ mkdir -p "$R/$1"; printf -- '---\nid: %s\ntitle: "x"\ntype: feature\nstatus: %s\nsize: M\npriority: P2\ndepends: [%s]\ncreated: 2026-01-01\n%b---\n' "$2" "$3" "$4" "$5" > "$R/$1/handoff.md"; }; mk alpha T-0001 ready cap:widget ""; mk beta T-0002 ready "" "provides: [widget]\n"; python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" roadmap && grep -F "| T-0001 |" "$R/roadmap.md" | grep -qF "| cap:widget (unmet) |"`
- `R=$(mktemp -d)/.sdlc; mk(){ mkdir -p "$R/$1"; printf -- '---\nid: %s\ntitle: "x"\ntype: feature\nstatus: %s\nsize: M\npriority: P2\ndepends: [%s]\ncreated: 2026-01-01\n%b---\n' "$2" "$3" "$4" "$5" > "$R/$1/handoff.md"; }; mk alpha T-0001 ready file:src/present.txt ""; mkdir -p "$(dirname "$R")/src" && touch "$(dirname "$R")/src/present.txt"; python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" roadmap && python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" check && grep -F "| T-0001 |" "$R/roadmap.md" | grep -qF "| file:src/present.txt |"`
- `R=$(mktemp -d)/.sdlc; mk(){ mkdir -p "$R/$1"; printf -- '---\nid: %s\ntitle: "x"\ntype: feature\nstatus: %s\nsize: M\npriority: P2\ndepends: [%s]\ncreated: 2026-01-01\n%b---\n' "$2" "$3" "$4" "$5" > "$R/$1/handoff.md"; }; mk alpha T-0001 ready file:missing.txt ""; python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" roadmap && python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" check && grep -F "| T-0001 |" "$R/roadmap.md" | grep -qF "| file:missing.txt (unmet) |"`
- `R=$(mktemp -d)/.sdlc; mk(){ mkdir -p "$R/$1"; printf -- '---\nid: %s\ntitle: "x"\ntype: feature\nstatus: %s\nsize: M\npriority: P2\ndepends: [%s]\ncreated: 2026-01-01\n%b---\n' "$2" "$3" "$4" "$5" > "$R/$1/handoff.md"; }; mk alpha T-0001 ready bogus ""; out=$(python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" check 2>&1); test $? -eq 1 && printf "%s\n" "$out" | grep -qF "alpha: depends entry 'bogus' is not T-NNNN, file:<path> or cap:<name>"`
- `R=$(mktemp -d)/.sdlc; mk(){ mkdir -p "$R/$1"; printf -- '---\nid: %s\ntitle: "x"\ntype: feature\nstatus: %s\nsize: M\npriority: P2\ndepends: [%s]\ncreated: 2026-01-01\n%b---\n' "$2" "$3" "$4" "$5" > "$R/$1/handoff.md"; }; mk alpha T-0001 ready file:/etc/hosts ""; out=$(python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" check 2>&1); test $? -eq 1 && printf "%s\n" "$out" | grep -qF "alpha: depends entry 'file:/etc/hosts' is not T-NNNN, file:<path> or cap:<name>"`
- `R=$(mktemp -d)/.sdlc; mk(){ mkdir -p "$R/$1"; printf -- '---\nid: %s\ntitle: "x"\ntype: feature\nstatus: %s\nsize: M\npriority: P2\ndepends: [%s]\ncreated: 2026-01-01\n%b---\n' "$2" "$3" "$4" "$5" > "$R/$1/handoff.md"; }; mk alpha T-0001 ready cap:nobody ""; out=$(python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" check 2>&1); test $? -eq 1 && printf "%s\n" "$out" | grep -qF "alpha: depends on cap:nobody, which no ticket provides"`
- `R=$(mktemp -d)/.sdlc; mk(){ mkdir -p "$R/$1"; printf -- '---\nid: %s\ntitle: "x"\ntype: feature\nstatus: %s\nsize: M\npriority: P2\ndepends: [%s]\ncreated: 2026-01-01\n%b---\n' "$2" "$3" "$4" "$5" > "$R/$1/handoff.md"; }; mk alpha T-0001 ready cap:widget ""; mk beta T-0002 ready T-0001 "provides: [widget]\n"; out=$(python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" check 2>&1); test $? -eq 1 && printf "%s\n" "$out" | grep -qF "dependency cycle T-0001 -> T-0002 -> T-0001"`
- `R=$(mktemp -d)/.sdlc; mk(){ mkdir -p "$R/$1"; printf -- '---\nid: %s\ntitle: "x"\ntype: feature\nstatus: %s\nsize: M\npriority: P2\ndepends: [%s]\ncreated: 2026-01-01\n%b---\n' "$2" "$3" "$4" "$5" > "$R/$1/handoff.md"; }; mk beta T-0002 ready "" "provides: widget\n"; out=$(python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" check 2>&1); test $? -eq 1 && printf "%s\n" "$out" | grep -qF "beta: provides 'widget' is not a list"`
- `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import tickets; sys.exit(0 if 'cap:<name>' in tickets.__doc__ and 'provides' in tickets.__doc__ else 1)"`
- `for l in "cap: edge orders after its provider" "file: entry that exists does not block" "malformed depends entry fails check" "unprovided cap: fails check"; do grep -qF "$l" plugins/sdlc-lite/scripts/tickets.py || exit 1; done`
- (guard) `B=$(mktemp -d); git show "$SDLC_BASE_SHA":plugins/sdlc-lite/scripts/tickets.py > "$B/tickets.py" && git show "$SDLC_BASE_SHA":plugins/sdlc-lite/scripts/order.py > "$B/order.py" && R=$B/x/.sdlc && mk(){ mkdir -p "$R/$1"; printf -- '---\nid: %s\ntitle: "x"\ntype: feature\nstatus: %s\nsize: M\npriority: P2\ndepends: [%s]\ncreated: 2026-01-01\n%b---\n' "$2" "$3" "$4" "$5" > "$R/$1/handoff.md"; } && mk alpha T-0001 ready T-0002 "" && mk beta T-0002 done "" "" && mk gamma T-0003 blocked "T-0001, T-0002" "" && python3 "$B/tickets.py" --root "$R" roadmap && cp "$R/roadmap.md" "$B/old.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$R" roadmap && cmp "$B/old.md" "$R/roadmap.md"` (T-only roadmap stays byte-identical to the base version's output; seen red on a copy whose render changes `none`)
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`

## Step 2: Document the depends forms and provides
level: L1
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
1. **`plugins/sdlc-lite/skills/handoff-format/SKILL.md`:**
   - In the front matter block, change the depends line to show `depends: [T-NNNN, file:<path>, cap:<name>, ...]`.
   - Add the line `provides: [name, ...]   # optional, capability names this ticket delivers` after `from:`.
   - In the paragraph after the block, add one or two sentences on what satisfies each form:
     - `file:` is repo-relative and met once the path exists; it never orders tickets.
     - `cap:` is met once a `done` ticket provides it, and orders the ticket after every provider.
     - `check` fails a malformed entry or an unprovided `cap:`.
2. **`plugins/sdlc-lite/skills/ticket/SKILL.md`:** add one Rules bullet stating the same forms, `provides:`, the `(unmet)` roadmap marking, and that a roadmap goes stale when a named file lands or a provider closes, so rerun `roadmap`.
3. **Templates:** in every template under `plugins/sdlc-lite/skills/ticket/templates/` with a `depends:` line, change only the trailing comment to name the forms, e.g. `# T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]`. Keep `depends: []` itself.
4. **`docs/maintenance/sdlc-internals.md`:** in the `scripts/tickets.py` entry, add one sentence describing the `file:<path>`/`cap:<name>` entries and `provides`.
### Acceptance criteria
- `grep -qF 'cap:<name>' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qE '^provides: .*optional' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'cap:<name>' plugins/sdlc-lite/skills/ticket/SKILL.md`
- `grep -qF 'provides:' plugins/sdlc-lite/skills/ticket/SKILL.md`
- `for f in plugins/sdlc-lite/skills/ticket/templates/*.md; do if grep -q '^depends:' "$f"; then grep -E '^depends:' "$f" | grep -qF 'cap:<name>' || exit 1; fi; done`
- `grep -qF 'cap:<name>' docs/maintenance/sdlc-internals.md`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`

## Step 3: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root. Fix any red that steps 1 and 2 introduced, keeping their behavior. If a skill body change makes generated Codex agents drift, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. A gate already red at the build-start HEAD is reported as `inherited red`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'`

## Risks
- **Unmet marks make the roadmap filesystem-dependent.** Rendering `(unmet)` for `file:` and `cap:` makes `check` report the roadmap stale when a named file lands or a provider closes. This is intended, but a lane that lands the file without rerunning `roadmap` will see `check` go red.
- **Path resolution picks the root.** `file:` paths resolve against the git toplevel of the ticket root. A ticket root in a different worktree resolves against that worktree, not main.
- **`cap:` validation.** `check` accepts a `cap:` that a non-done ticket provides. It only orders after that ticket and marks the entry unmet. This follows the handoff's "like a dangling id" default.
- **Existing tickets.** A ticket that already holds a non-`T-NNNN` depends entry used to fail check as dangling. It now fails with the malformed-entry message instead. The failure is the same, the message is different.
- **Runtime.** `check.sh` takes about 2 minutes.
