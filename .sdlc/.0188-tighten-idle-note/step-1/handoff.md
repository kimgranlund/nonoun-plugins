## Task goal
Make `docs/validation/messages-idle-host-limit-2026-10-01.md` say that `wait` does not address the idle-host limit and the watcher, which is designed but not built, is what would.

## Step 1: Fix the one sentence
level: L1

### Do
Edit only `docs/validation/messages-idle-host-limit-2026-10-01.md`. Replace the sentence "T-0181 adds a blocking `wait` command and T-0182 designs an external watcher; both address this limit." with: "T-0181 adds a blocking `wait` command, which is cheaper than a polling subagent but still returns only into a running parent turn, so it does not address this limit. T-0182 designs an external watcher that would resume an idle host; it is a design only and is not built." If any other sentence in the file says or implies that `wait` wakes an idle host, fix it the same way. No em dashes.

### Acceptance criteria
- `! grep -q 'both address this limit' docs/validation/messages-idle-host-limit-2026-10-01.md`
- `grep -q 'does not address this limit' docs/validation/messages-idle-host-limit-2026-10-01.md`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "docs/validation/messages-idle-host-limit-2026-10-01.md" | { ! grep -q .; }`
