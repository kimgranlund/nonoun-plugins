<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
In numbered mode, make the `tickets.py` reference scan (`close` and `archive`) count the literal `<rel>/<slug>` only where it starts a path token. That way another tree's `other/.sdlc/0003-x`, `/elsewhere/repo/.sdlc/0003-x`, and `../other/.sdlc/0003-x` are neither reported nor rewritten, and every cite that really points at the folder still is.

## Step 1: Token-start boundary for the literal reference rule, with selftest cases and docs (gates green)
level: L3
### Do
1. In `plugins/sdlc-lite/scripts/tickets.py`, change `literal_re(old)` so the literal matches only at the start of a path token.
   - It must start at the start of the text, or right after a character that `TOKEN_RE` treats as a delimiter: whitespace, `'`, `"`, backtick, `(`, `)`, `<`, `>`, `[`, `]`. For example, use a lookbehind such as `(?<![^\s'"`()<>\[\]])`.
   - Keep the existing trailing lookahead `(?![A-Za-z0-9_-])`, which is the T-0128 fix for `.sdlc/0003-xy`.
   - The boundary must live inside `literal_re`, because `outside_refs` and `rewrite_files` both use it. Acceptance criterion 4 monkeypatches `literal_re` back to the old body to prove the new selftest cases bite.
   - Do not change `ref_tokens`. A token like `./.sdlc/0003-x`, or this toplevel's absolute path, still counts because `ref_tokens` resolves it to the folder.
2. Add selftest cases in `selftest()`:
   - In the close `(u) refs` block, next to the existing "negative controls: a bare word and a path resolving elsewhere" case, prove that each of these neither blocks `close` nor gets rewritten by `close --rewrite-refs` (file bytes unchanged, `rewrote` not in the output):
     - `other/.sdlc/0003-x/handoff.md`
     - an absolute path into another directory ending in `.sdlc/0003-x/...`, such as `/elsewhere/repo/.sdlc/0003-x/handoff.md`
     - `../other/.sdlc/0003-x/handoff.md`
   - Add a close case where one file cites both `other/.sdlc/0003-x/a.md` and the real `.sdlc/0003-x/b.md`. `--rewrite-refs` must rewrite only the real cite.
   - Add the same pair of cases (other-tree paths alone, and mixed with a real cite) in the `archive refs` block, using `other/.sdlc/0001-alpha/...` forms.
   - Keep every existing case unchanged.
3. Update the docstrings of `literal_re`, `outside_refs`, and `rewrite_files` to state the rule. Use the exact phrase `starts a path token`, for example: "the literal counts only where it starts a path token (start of text or after a TOKEN_RE delimiter)". Also update the close/archive `--rewrite-refs` help text only if it describes the literal rule (today it does not).
4. Add the phrase `starts a path token` to each doc's description of the literal rule. Also note the limitation that a URL or prefixed form (`https://.../.sdlc/0003-x`, `key=.sdlc/0003-x`) is no longer a reference.
   - `CLAUDE.md`, Layout `scripts/tickets.py` bullet: the sentence "The scan finds the folder name, then keeps files with a literal `<rel>/<slug>` ...".
   - `.claude/agents/sdlc-lite-author.md`: the reference-scan passage for tickets.py.
   - `plugins/sdlc-lite/skills/ticket/SKILL.md`: the sentence "The scan finds the folder name, then keeps files with a literal `<rel>/<slug>` ...".
5. This is the gates green step. Run `plugins/sdlc-lite/scripts/check.sh` and fix any red this step introduced.

Criterion 1 uses a temporary directory outside the tree. None of the criteria change the tree.
### Acceptance criteria
- Other-tree paths are not references. `outside_refs` returns no files for a file citing only other-tree paths:
  `python3 -c 'import sys,pathlib as p,tempfile,subprocess as s;sys.path.insert(0,"plugins/sdlc-lite/scripts");import tickets as t;d=p.Path(tempfile.mkdtemp());(d/".sdlc/0003-x").mkdir(parents=True);s.run(["git","init","-q",str(d)]);(d/"a.md").write_text("see other/.sdlc/0003-x/h.md and /elsewhere/repo/.sdlc/0003-x/h.md and ../other/.sdlc/0003-x/h.md\n");r=t.outside_refs(d/".sdlc","0003-x");print(r[3]);raise SystemExit(r[3]!=[])'`
- A mixed file gets only its real cite rewritten:
  `python3 -c 'import sys,pathlib as p,tempfile,subprocess as s;sys.path.insert(0,"plugins/sdlc-lite/scripts");import tickets as t;d=p.Path(tempfile.mkdtemp());(d/".sdlc/0003-x").mkdir(parents=True);s.run(["git","init","-q",str(d)]);f=d/"a.md";f.write_text("see other/.sdlc/0003-x/h.md and .sdlc/0003-x/h.md\n");top,o,n,fs=t.outside_refs(d/".sdlc","0003-x");t.rewrite_files(top,fs,o,n);g=f.read_text();print(fs,repr(g));raise SystemExit(not(fs==["a.md"] and g=="see other/.sdlc/0003-x/h.md and .sdlc/.0003-x/h.md\n"))'`
- (guard) Real cites are still found: a bare token at the start of the text, one in backticks, one after `(`, one in double quotes, and this toplevel's absolute path. This goes red when the slug does not match:
  `python3 -c 'import sys,pathlib as p,tempfile,subprocess as s;sys.path.insert(0,"plugins/sdlc-lite/scripts");import tickets as t;d=p.Path(tempfile.mkdtemp());(d/".sdlc/0003-x").mkdir(parents=True);s.run(["git","init","-q",str(d)]);w={"a.md":".sdlc/0003-x/h.md\n","b.md":"see "+chr(96)+".sdlc/0003-x"+chr(96)+"\n","c.md":"[x](.sdlc/0003-x/h.md)\n","e.md":"see \".sdlc/0003-x/h.md\"\n","f.md":"see "+str(d)+"/.sdlc/0003-x/h.md\n"};[(d/k).write_text(v) for k,v in w.items()];r=t.outside_refs(d/".sdlc","0003-x");print(r[3]);raise SystemExit(r[3]!=sorted(w))'`
- Red before, green after: with `literal_re` patched back to the pre-change body, the new selftest cases fail (selftest returns 1):
  `python3 -c 'import sys,re,io;sys.path.insert(0,"plugins/sdlc-lite/scripts");import tickets as t;t.literal_re=lambda old: re.compile(re.escape(old)+r"(?![A-Za-z0-9_-])");sys.stderr=io.StringIO();rc=t.selftest();sys.stderr=sys.__stderr__;print("rc",rc);raise SystemExit(rc!=1)'`
- The close selftest cases exist: `grep -qF "other/.sdlc/0003-x" plugins/sdlc-lite/scripts/tickets.py`
- The archive selftest cases exist: `grep -qF "other/.sdlc/0001-alpha" plugins/sdlc-lite/scripts/tickets.py`
- The docstrings state the rule: `grep -qF "starts a path token" plugins/sdlc-lite/scripts/tickets.py`
- `grep -qF "starts a path token" CLAUDE.md`
- `grep -qF "starts a path token" .claude/agents/sdlc-lite-author.md`
- `grep -qF "starts a path token" plugins/sdlc-lite/skills/ticket/SKILL.md`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `plugins/sdlc-lite/scripts/check.sh`

## Risks
- The new boundary drops some forms that used to count as references: URLs, `key=` forms, and `./.sdlc/0003-x` cited from a subdirectory file (which does not resolve to the folder anyway). The handoff accepts this and asks for the limitation to be documented. A reviewer may still expect those forms to be caught.
- Criterion 4 depends on the fix living in `literal_re` and on `selftest()` running in-process through the module-global `literal_re`, which it does today. A builder who puts the boundary somewhere else would fail that criterion even if the behavior were correct.
- `check.py` may enforce that `CLAUDE.md` and `sdlc-lite-author.md` stay in sync on this passage. The final `check.sh` guard catches that.
