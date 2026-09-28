<!-- role=builder level=L1 model=sonnet effort=low -->
Scope matches exactly (check-this-repo-s-live and add-close-to-tickets-py had no diff, expected since titles already correct). No commit made, per constraints.

## Status
done

## Changes
plugins/sdlc-lite/scripts/tickets.py: added `follow_up_title` helper, used it in `cmd_close`, added selftest fixture bullet and assertions
.sdlc/.0007-run-the-filer-headless-on/handoff.md: retitled T-0007
.sdlc/.0009-optional-id-and-status-columns/handoff.md: retitled T-0009
.sdlc/.0010-t-0001-still-shows-status/handoff.md: retitled T-0010
.sdlc/.0011-bring-this-repo-s-backlog/handoff.md: retitled T-0011
.sdlc/roadmap.md: regenerated

## Checks
`python3 plugins/sdlc-lite/scripts/tickets.py selftest` before fix: FAILED with `(a) short-first-sentence bullet title is the sentence without its final period` and `(a) long_item title is a whole-word prefix of long_item...` — captured above.
`python3 plugins/sdlc-lite/scripts/tickets.py selftest` after fix: `tickets selftest: PASS`
`plugins/sdlc-lite/scripts/check.sh`: passed (`ok: 18 role levels...`, `selftest: PASS`, `tickets selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`)
`python3 plugins/sdlc-lite/scripts/tickets.py check`: `ok: 13 tickets, roadmap current`
Verified `.sdlc/roadmap.md` T-0007..T-0012 rows: no title ends in a partial word before `...`; all <= 70 chars
`git diff --stat`: touches only `plugins/sdlc-lite/scripts/tickets.py`, four of the six ticket handoffs (T-0008 and T-0012 needed no change, their titles were already correct), `.sdlc/roadmap.md`, plus untracked `.sdlc/0013-follow-up-titles-truncated/`

## Notes
T-0008 (`check-this-repo-s-live`) and T-0012 (`add-close-to-tickets-py`) titles were already correct under the new rule, so their `title:` lines are unchanged (not in `git diff --stat` output). This matches the acceptance criterion's intent (no title ending in a partial word) even though the handoff listed all six files as targets.
