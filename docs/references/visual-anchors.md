# Visual anchors

The closed emoji set for chat replies of the author agent and the session `report`. One anchor per line, first character of the line, followed by the item and the reason. The set carries meaning only. It is not used in code, commit messages, tickets or documents. `rag-board` uses the same four state glyphs. Source of the rule: `.claude/agents/nonoun-author.md` (Output, line 3) and `docs/planning/author-output-block-draft.md`.

| Group | Anchor | Means | Example line |
|---|---|---|---|
| State | 🟢 | done, ok | 🟢 T-0452 merged and closed |
| State | 🟡 | needs a look, nothing lost yet | 🟡 T-0450 stalled at planning |
| State | 🔴 | blocked, cannot proceed | 🔴 gate timed out, rc 3 |
| State | ⏳ | waiting on a role, gate or person | ⏳ verifier L2 running 11 minutes |
| Direction | 👉 | the one next action | 👉 Run `check.sh` |
| Direction | ❓ | a decision for the user | ❓ Push main fast-forward? |
| Direction | 🔁 | retry, replan or second round | 🔁 verifier round 2 after one fix |
| Event | 🏆 | a win: a measure moved the right way or a goal was met | 🏆 K-002 lost minutes 1364.7 to 0 |
| Event | 🚀 | shipped: released, pushed or published | 🚀 v0.22.4 published |
| Event | 🔀 | merged into main or an integration branch | 🔀 wave 38 merged |
| Event | 🎫 | a ticket filed | 🎫 T-0466 filed |
| Event | 🧹 | cleanup done, lanes or branches removed | 🧹 6 lanes archived |
| Guard | ⚠️ | a likely problem, with its likely cost | ⚠️ gate lock may time out again |
| Guard | 🛑 | stopped on purpose by a rule or cap, state written | 🛑 budget cap reached at $7.94 |
| Guard | 🐛 | a defect or failing check found | 🐛 selftest flakes under peer load |
| Guard | 🔑 | needs the user's authorization | 🔑 publish needs your go |
| Measure | 📊 | a metric reading | 📊 K-005 first pass 89 of 123 |
| Measure | 💰 | cost or budget | 💰 $5.99 of $10 |
| Measure | ⏱️ | duration or time estimate | ⏱️ about 15 minutes |
| Measure | 🧪 | an experiment, replay or A/B | 🧪 overlay A/B: no change |

## Rules

- At most 8 anchored lines per reply; a reply with no state to report has none.
- Never two anchors on one line, never an anchor with no text after it, never an anchor mid-sentence.
- Pick the narrowest meaning: a win is 🏆 and not 🟢; a deliberate stop is 🛑 and not 🔴; a likely problem is ⚠️ and not 🟡.
- A new anchor joins the set only with a measured use. `reply_lint.py` (T-0466) counts each anchor's use; one unused for 14 days is a candidate to remove.
