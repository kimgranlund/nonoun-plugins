## Goal
A running watcher loop and the entry-file hint call messages.py through a path that survives a plugin update.

## Intent
Literal ask: messages.py has no version-free entry point, so a watcher breaks when the plugin cache updates.
Deltas:
- missing Do: defaulted: find every shipped text that names a versioned cache path to messages.py and point it at one version-free resolve step
- missing done-condition: defaulted: a guard that fails on a versioned cache path, observed failing first
Do: replace each versioned `sdlc-lite/<x.y.z>/scripts/messages.py` path in the shipped entry files and skill texts with one documented resolve step, and add a selftest case for it.
Level: L2 (lane: solo; cost: low, a few text edits and one guard; reversible: yes)
Non-goals: model or effort changes; running onboard in consumer repos.
Done when:
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/messages.py selftest` exits 0
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py` exits 0, with the new versioned-path guard observed red before the edit
