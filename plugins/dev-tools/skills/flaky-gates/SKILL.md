---
name: flaky-gates
description: >-
  Decides whether a RED test gate can be trusted on a host running concurrent agents and
  builds: reap orphaned browser/compiler processes first, then separate contention from
  regression with red-under-load vs green-in-isolation. Use when the tests are flaky, red
  in CI but green locally, a different set of tests fails every run, the suite went slow or
  started timing out, load average is huge, or someone asks "can I trust this red". NOT for
  fixing a test that fails in isolation too (the seat that owns the code); NOT for
  port-squatting dev servers (port-zombie-sweep owns PORT squatters, this owns CPU zombies).
disable-model-invocation: false
user-invocable: true
---

# flaky-gates

A red gate on a loaded host is a claim about the host, not yet about the code. This decides
which one it is, in a fixed order — machine first, then the evidence pair, then the flake
mode — and a red never reaches a fixing seat until that order has run.

Two invariants:
- **MUST NOT hand a file to a seat to "fix" on the strength of a contended run.** A file
  named only by a loaded run is a suspect, not a defect.
- **MUST NOT judge a gate by its output text.** The exit code is the verdict.

## 1. Reap the machine before reading anything

Orphaned test-browser processes outlive the run that spawned them and never exit. Measured
2026-07-29: two `WebKit.WebContent.xpc` processes parented to launchd (ppid 1) at 124% and
101% CPU for ~5h, 1.8 GB RSS each — ~2.5 cores of permanent load. Reaping them dropped load
average 173 → 4.4, and the SAME commit went 891s-red → 64.65s-green. A 14× spread with a
zero-byte diff: nothing measured before the reap means anything.

```sh
ps -axo pid,ppid,%cpu,rss,etime,comm | grep -Ei 'WebKit|Chromium|node|tsc' | awk '$2==1'
uptime
```

An orphan is: ppid 1 + hours of accumulated CPU + growing RSS + no live test runner to own
it. All four, before any kill. Anything short of all four gets reported, not killed.

## 2. The process-count check lies twice — pair it with load

`ps aux | grep -c '[v]itest'` is the reflex, and it is wrong in two measured ways: it
**self-matches** when the surrounding command line contains the literal string (a sibling's
wait loop, or your own `echo "vitest done"` — the `[v]` trick hides the grep itself and
nothing else), and it has a **blind spot** — a measured load of 82.7 read as ZERO because the
load was `tsc` at 141% plus WebKit orphans, no vitest at all.

```sh
ps aux | grep '[v]itest' | grep -v 'grep -q' | grep -vc 'shell-snapshots'
uptime
```

Both, always. **A zero count with a high load average is still contention** — believe the
load average.

## 3. The evidence pair that settles it

Red-under-load + green-in-isolation = contention. Red in isolation = regression, route it.

The contention signature is **a different set of files failing each run**. Three trials with
zero overlap between any pair is contention, proven; the same file failing three times is a
defect, and the count of failures is irrelevant next to which files they are.

Run the isolation leg on a reaped, quiet machine, in the foreground, one shard, no siblings.

## 4. Exit-code discipline

- Never pipe a gate. `npm test | tail -20` reports the exit code of `tail`; a red gate reads
  green. Run it bare, read `$?`.
- A wrapper `cmd; echo "EXIT=$?"` always exits 0 itself, so a background-task notification
  reports the WRAPPER's success. Read the printed `EXIT=` value; never the notification's
  status line.

## 5. Two flake modes, two different remedies

| Mode | Symptom | Remedy |
|---|---|---|
| **A — the runner's bound is short** | `Test timed out in Nms` | Raise the per-file timeout, for the scheduler-waiting class only. Never globally: a genuine hang then takes 2× longer to surface, which is accepted for that class alone. |
| **B — the test's own bounded wait false-settles** | a NORMAL assertion fails, reading exactly like a real regression | No timeout raise reaches this. The wait helper is the defect — it exhausted its budget and returned a stale value as if settled. Fix the helper. |

Mode B is the expensive one: it wears the costume of a regression. A red assertion inside a
file that also carries a bounded wait gets the helper's exhaustion path read before the
assertion is believed.

## 6. Prevention

Stagger gate-heavy seats — one seat's full browser suite poisons every sibling's gates for
its whole duration. Sequential shards exist for this reason; a seat that backgrounds its
suite and moves on has handed the next seat a contended machine.

## 7. Layer coverage — a green gate proves only the layers it runs

"Gates green" is a claim about the LAYERS the gates exercise, nothing more. Two measured
instances, one night (agent-ui, 2026-08-13):

- **The unexercised layer**: the docs-site deploy was red for 16 straight pushes while
  `check`/`test` stayed green throughout — only the wrangler Worker bundler resolves the
  `node:fs` alias to `fs-shim.ts`, and no standing gate ran that bundler, so a missing
  `statSync` export was invisible until deploy time (agent-ui #811). The first diagnosis
  probe repeated the mistake: `npm run build` (the SITE build) exited 0 — wrong layer,
  the Worker bundle was the red one. Remedy shape, both halves: a one-shot probe at the
  failing layer itself (`wrangler deploy --dry-run` — the exact step that fails), then a
  TRIP-WIRE test that drags the failure class into a layer the standing gates DO run
  (every `node:fs` named import in the aliased modules must be a shim export — now red in
  `npm test`, not at deploy).
- **The proxy layer**: a blocked lane re-checked its external dependency four times over
  two months by watching an upstream ISSUE's open/closed state — while the artifact the
  lane actually waited on (the `/conformance/suites/*.yaml` convention) had been live on
  that repo's main since June (agent-ui #616; the issue tracked an ADDITIONAL suite, not
  the convention). A tracker's status is a proxy, and proxies rot silently: probe the
  artifact — the directory listing, the API response, the file's bytes — never the
  tracker row that talks about it.

State a gate verdict with its coverage: "check+test green (deploy pipeline not exercised)"
is honest; "gates green" alone is the claim that bit both times.

Cross-links: a check that can never go red is a different defect →
[[checks-that-bite]]. Dev servers holding a port → [[port-zombie-sweep]].
