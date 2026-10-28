# Step handoff rules

Detail for the handoff-format skill's `## Step handoff` section.

## Other writers

`steps.py swap` is the one other writer: it rewrites one criterion line from the verifier's `swap old:`/`swap new:` pair after a `plan defect:` fail (/chain 4.8), never by hand, and it refuses a new text whose bracket clause differs from the old line's. `steps.py amend` rewrites one criterion line the same way from a blocked builder's `amend old:`/`amend new:` pair on an unbuilt step (/chain 4.10) and itself appends `amend applied: step <n>: ...` under `## Plan review`, the task's one replan. `steps.py widen` widens the scope criterion with conductor-allowed paths (/chain 4.9) and appends one item per path to a `## Scope widened` section at the end of the step handoff: ``- `<path>`: allowed by a conductor scope decision (steps.py widen)`` (with `--reason "<why>"`, `: <why>` follows; a step with no scope criterion takes the paths and reason as the recorded allow-list only with `--reason`).

## Base commit

A step handoff may name the commit its build starts from with a line `base: <sha>` (a bare line or a list item); it must be a commit that is an ancestor of HEAD. The runner, `dispatch.py prepare`, and `steps.py` take the step's `SDLC_BASE_SHA` in this order: the named base, else the sha recorded in `base-sha` at the step's first dispatch (so a rework keeps its original base), else HEAD of the execution tree (the owned lane worktree when the handoff is in the main checkout and the cwd is that lane), never the main checkout's HEAD. In a lane, `dispatch.py prepare verifier` with nothing named or recorded (a lane resumed after its driver died) takes the lane start instead (its `.lane.json` `base_sha`, else its fork point), since the lane HEAD is then the driver's own WIP commit. A verifier in a host worktree (`.claude/worktrees/<leaf>`, a `fanout.py prep` solo lane) with nothing named takes the commit the host cut it from, its merge base with the remote default branch, not prep's recorded base, so its diff holds only the lane's change. A caller-supplied `SDLC_BASE_SHA` that differs from that pick is refused with a `SDLC_BASE_SHA refused:` line; naming it in the handoff is the way to use it.

## Declared regression tests

A step handoff with a `(red)` criterion may declare the regression tests the build writes first with a line `tests: <path>, <path>` (a bare line or a list item; exact repo-relative files, no directory, glob, absolute path, or `..`; `steps.py lint` refuses those). `redck.py record` hashes a declared test that is dirty into the control as a prelude (sha256 per path) and still records `pre-edit` when no other path differs from the base; any other dirty path, an undeclared test file included, makes it `retrospective`. `redck.py audit` reports `prelude-changed` (a process deviation) when a declared test no longer matches its stored hash, so the test cannot be edited to fit the implementation after the red control.

## Parity criteria

A styling approval is a `(parity)` criterion: ``- (parity) `<capture command>` writes `<real.png>`; against `<mock.png>`: <property>, <property>`` (the project's own capture command and mockup; at most five named properties such as column count, gutter, a filled primary button, the heading order, never "matches"). `steps.py lint` refuses a `(parity)` line with fewer than two image paths or no property list. The verifier runs the capture as an observed run, reads both images, and records pass or fail per property; a difference no property names is a note. A styling ticket writes `verifier: L3` when the owner wants it.

## Evidence

Evidence. Screenshots, captures and other binary evidence (png, jpg, jpeg, gif, webp, mp4, mov, webm, zip, pdf), a `(parity)` capture included, go to the user-cache dir `wtroot.py evidence <ticket>` prints (`<user cache>/sdlc-lite/<repo key>/evidence/<ticket>/`, kept across reboots and never swept), never into the repo or `.sdlc/`; the Outcome or the notes cite the path. Traces are kept only when the ticket asks for them or a failure needs them, as text under the records dir. `tickets.py check` warns on each tracked binary under `.sdlc/`.

## Read first

`### Read first` is optional. For each file the step changes, it lists the nearest `AGENTS.md` in that file's folder or a folder above it, leaving out the root entry, one ``- `<path>` `` line each, relative to the repository root. A step whose only entry is the root has no `### Read first`. It also lists the routed skill of each changed file: a list item or table row in any `AGENTS.md`, root included, that pairs a path or glob with one skill path (a `SKILL.md` or a folder under `skills/`) routes files under that path to the skill, listed even when the root is the only entry. The step cites the skill section instead of restating its rules. `steps.py lint` refuses a listed path that does not exist, and a step whose scope criterion names a routed path without its skill listed.

## Cited paths

`steps.py lint` refuses any cited `.sdlc/...` path that does not exist, except a path the step creates or one from another repository. A created path is declared by a ``[creates: <path>]`` marker, an `Outputs: <path>` line, a create or write verb on a `### Do` line, or a code span of a `(red)` criterion; a path an earlier step declares that way is also exempt in later steps, in a cited path and in `### Read first`. The refusal for a missing path names the ``[creates: <path>]`` marker and the `Outputs:` line as the fix. A foreign path is declared by an `Other repo: <name>` line with the path written as `<name>/.sdlc/...`; an absolute path outside the repository needs no line.

## Merge step conflict-marker guard

The conflict-marker guard flags only `++` lines of `git diff-tree --cc HEAD`, so a kept marker line textually identical to a parent line that aligns with it (shown as `+ ` or ` +`) passes. This is accepted, because no one-line guard separates it from a legit lane line in a file both sides changed. The builder must still resolve every conflict, and the check.py probe pins the miss.

## Previous attempt

`## Previous attempt` is appended by /chain 4.4 only after a verifier fail that is not a plan defect (its For the next attempt does not start with `plan defect:`). A blocked builder or a `plan defect:` fail goes to a replan instead, and the step handoff is rewritten by `steps.py split`, not appended to. A swapped plan defect (a `plan defect:` fail whose criterion `steps.py swap` replaced) rebuilds at the same level without `## Previous attempt`.
