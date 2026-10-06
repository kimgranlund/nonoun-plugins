<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - Resolver: `import collections`, `LAYOUT_RE`, `LayoutPaths`, `layout_lines(root)` and `layout_paths(root)`. `layout_paths` calls `ticket_dir`; `ticket_dir` is unchanged apart from its docstring.
  - Every `cmd_*` now gets `td` from `layout_paths(root).tickets`, so a bad `layout` line is refused before any write.
  - Callers:
    - `render` sets the roadmap link prefix from `tickets == roadmap.parent`.
    - `write_roadmap` (creates the folder first) and `stale` use `layout_paths(root).roadmap`.
    - `append_notes` writes `layout_paths(root).notes` and creates its folder.
    - The three `outside_refs` calls pass `layout_paths(root).roadmap`.
  - Router:
    - New constants `ROUTER_FLAT_INTRO`, `ROUTER_TOPICS_INTRO`, `WORK_TEMPLATE` and `NOTES_TEMPLATE`.
    - `router_files` adds the work/ and notes/ AGENTS.md and CLAUDE.md files under topics.
    - Under topics, `router_bodies` swaps in the topics intro, rewrites ``go to `notes.md` `` to ``go to `<R>/notes/notes.md` `` in the root and tickets bodies, and returns the work and notes blocks.
    - Flat output is byte-identical.
  - Strays: `ROOT_ALLOWED` and `root_strays(root)`, called only from `cmd_check`.
  - Flat warning: `cmd_check` appends the migrate-layout warning last when the layout is flat and the config has no `layout:` line.
  - Selftest:
    - New topics cases: new, close, the allowed root entries, three stray controls, three bad-config controls (topics without `ticket_root`, `nested`, both values), a stale `work/AGENTS.md`, the `layout: flat` opt-out, and git-backed close and archive scans that skip `tickets/roadmap.md`.
    - The three exact `ok:` asserts are updated to the new flat output.
  - Docstrings: the module usage text (`--root`, `roadmap`, `check`, `config`, the Router section, the roadmap writer line) and the `ticket_dir` docstring.

## Checks
- All acceptance criteria 1-9 plus the two fixture guards (base-archive flat/nested `check` and the scope guard), run verbatim through one script.
  - First run, before the selftest edits: everything passed except criterion 9, which was expected.
  - Final run: all PASS.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS, about 33 s. Run twice: after the selftest edits and after the docstring edits.
- Negative control: replacing `root_strays` with `lambda r: []` turns the selftest red (rc=1). The three topics stray cases fail (stray dir, root `notes.md`, root `.NNNN-x`).
- `git diff --check`: clean.
- `git status --short --untracked-files=all -- . ':(exclude).sdlc'`: only `plugins/sdlc-lite/scripts/tickets.py` modified.
- No pre-build base check was needed, because no gate went red.

## Notes
- I also changed two selftest asserts the handoff did not list, in the numbered-config warning block (about lines 2033-2036). They checked `'warning' not in out + err` on flat fixtures, which goes red now that every flat root warns. They now check `'ticket_folders: numbered' not in out + err`, the warning those cases actually test.
- This repo's own `.sdlc/config` has no `layout:` line, so `tickets.py check` here now prints the migrate-layout warning on every run (exit stays 0). The other callers in `check.py`, `evals.py` and `proposals.py` read only the exit code. The planner should decide whether T-0206/T-0207 adds `layout: flat` to this repo or migrates it.
- `ROUTER_FLAT_INTRO` repeats the first paragraph that still sits inside `ROUTER_TEMPLATE`, and `router_bodies` swaps the two by string match. If one is edited without the other, a topics tree keeps the flat paragraph. The `tp-new` selftest case catches that by checking for `tickets/roadmap.md` in the root block.
- The two-values error reads `<config>: layout: topics conflicts with layout: flat; keep one layout value; nothing written`. It names the first line that differs from the first `layout` line.
- Nothing is committed.
