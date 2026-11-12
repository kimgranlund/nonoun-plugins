# Worked example: a shorter route that misses governing context

This authored UI corpus has two tasks: edit a menu and look up status. The menu
must preserve keyboard navigation; that acceptance rule is fixed in suite.json.

registry-before.json omits the menu's governing edge. Its one-read menu route looks
cheap but fails acceptance. registry.json adds the required policy without changing
the files or suite. A separate status lookup must stay passing without reading the
menu, policy or billing branch. A known-ID alias exercises direct entry.

From the skill root (replace output paths with fresh destinations):

```sh
python3 scripts/validate.py --root examples/worked-corpus --registry examples/worked-corpus/registry.json
python3 scripts/replay.py --root examples/worked-corpus --registry examples/worked-corpus/registry-before.json --suite examples/worked-corpus/suite.json --out /tmp/pc-before.json
python3 scripts/replay.py --root examples/worked-corpus --registry examples/worked-corpus/registry.json --suite examples/worked-corpus/suite.json --out /tmp/pc-after.json
python3 scripts/replay.py compare --before /tmp/pc-before.json --after /tmp/pc-after.json
```

The before command is expected to exit 1 (one of three cases passes); after exits
0 (three of three). The repaired menu route uses two reads instead of one because
correctness requires the governing policy. Submission/retention remain unknown.
No model, provider key, external command or network is involved in this replay.
Tests mutate temporary copies for drift, ambiguity, missing sources, cycles,
conflicts and budgets; the shipped acceptance suite remains unchanged.
