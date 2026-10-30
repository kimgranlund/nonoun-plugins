<!-- role=verifier level=L2 model=fable effort=medium -->
## Verdict
pass

## Criteria
- command-modal browser file exits 0, 2 files, 0 failed: pass. Evidence: `npx vitest run --config vitest.browser.config.ts --project packages .../command-modal/command-modal.browser.test.ts` → `Test Files 2 passed (2)`, `Tests 30 passed (30)`, `EXIT=0` (run twice, 11:20 and 11:25, both green).
- Throwaway geometry probe exits 0 with 4 passed, no `zz-*` left: pass. Evidence: probe written in a throwaway worktree (`/tmp/verif-cmdmodal-wt`, HEAD + `git apply` of the working-tree diff), same mount pattern, two cases (`zzzz-no-match` typed → 0 visible options; 40-option list → `scrollHeight > clientHeight`), each asserting `footer.height > 0`, `footer.top >= list.bottom - 1`, `footer.bottom <= dialog.bottom + 1` → `Test Files 2 passed (2)`, `Tests 4 passed (4)`, `EXIT=1`→ no, `EXIT=0`. Negative control: `git apply -R` the diff in the same worktree → `Tests 4 failed (4)`, all `no [data-part="footer"] rendered: expected null not to be null` (chromium ×2, webkit ×2), `EXIT=1`. The biting variable is the footer's existence in the DOM. Worktree removed; `ls packages/agent-ui/components/src/controls/command-modal/ | grep -c '^zz-'` → `0`; `git worktree list | grep -c verif` → `0`.
- Scoped shard (controls + dom + traits) exits 0 with ≥2000 tests: pass. Evidence: first run at load ~64 exited 1 with 4 timeouts (command-modal chromium+webkit "typing filters the list", combo-box webkit "appended WHILE OPEN", popover webkit "default placement=bottom-start", all `Test timed out in 15000ms` / `Hook timed out in 30000ms`). Each file rerun alone: combo-box `112 passed EXIT=0`, popover `20 passed EXIT=0`, command-modal `30 passed EXIT=0`, so contention per the handoff rule. Shard rerun at load ~33: `Test Files 170 passed (170)`, `Tests 2404 passed | 2 skipped (2406)`, `EXIT=0`. 2406 ≥ 2000.
- `find ... -maxdepth 1 -name '*.browser.test.ts'` prints only site-nav: pass. Evidence: output was exactly `packages/agent-ui/components/src/site-nav.browser.test.ts`.
- Pre-existence of the omitted red, both checks: pass. Evidence: `node -e "...filter(e=>e.section==='Components'&&!e.group).length===0..."` → `exit=0`; `git status --short -- site/sitemap.json site/pages/_page.ts .../site-nav.browser.test.ts` printed nothing. Source confirmed: `site/pages/_page.ts:1121` `const key = entry.group ?? entry.section`; `site-nav.browser.test.ts:92` `expect(labels).toContain('Components')`.
- site-nav file exits 1 with exactly 2 failed of 6, both the context-labels title: pass. Evidence: `Test Files 2 failed (2)`, `Tests 2 failed | 4 passed (6)`, `EXIT=1`; both `×` lines titled `renders section context-labels and the wide name|tag row (proper name + trailing data-role="tag")` (chromium + webkit), `AssertionError: expected [ 'Feed & status', …(23) ] to include 'Components'`.
- `npm run check` exits 0: pass. Evidence: `EXIT=0`, tail ends `selftest: all green`.
- `git status --short | grep -v '^?? .sdlc'` lists exactly the seven files and no `*.test.ts`: pass. Evidence: output is the seven `M` lines (lld, command-modal.css/.md/.ts, dogfood-assets.ts, theme-provider-built.css, llms-full.txt); `grep -c 'test\.ts'` → `0`. The else-branch (npm test + regen freshness) therefore does not apply.
- `git diff command-modal.ts` touches no `static props` line: pass. Evidence: `git diff ... | grep -n 'static props'` → `grep exit=1` (no match); the diff hunks are the header comment, `#footer` field, `#ensureParts` guard, footer construction, and `modal.append(search, status, list, footer)`.
- Builder Notes name the site-nav red, cause, and HEAD `220ae0ac`: pass. Evidence: `builder-L3.md` §Notes names the file, the full test title, the line-92 assertion, `entry.group ?? entry.section` (line 1121) + commit `6ea5c5e3` / GH #1616, and "reproduces at HEAD `220ae0ac`"; `git rev-parse --short HEAD` → `220ae0ac`.

## Out of scope changes
None. Working tree holds only the seven files named in Do; no test files, no `zz-*` probe, no `site/pages/_page.ts` or `site/sitemap.json` change.

## For the next attempt
None.
