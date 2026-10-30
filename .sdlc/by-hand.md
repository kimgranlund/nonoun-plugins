<!-- sdlc:managed:start v1 sha256:c029de6360b6 -->
# Working by hand

Use this file when the SDLC plugin is not installed: it creates, claims, releases and closes a ticket with git and a POSIX shell. Run each block from the repository root after replacing `T-NNNN` and `NNNN` (the ticket id), `<slug>`, `<title>`, `<by>` (your name), `<one line>` and `YYYY-MM-DD` (today). `tickets.py roadmap` generates this block: do not edit inside it. `docs/work/ROADMAP.md` and the routers stay stale until the next plugin run regenerates them.

## New

The first command prints the highest id in use; the new id is one above it (T-0001 when it prints nothing). The second reserves the id: a non-zero exit means another worktree took it, so add one and run it again. `type:` is feature, bug, chore, spike or idea. Then fill in the sections.

```sh
{ find docs/work -maxdepth 2 -name handoff.md -exec sed -nE 's/^id: T-([0-9]{4}).*/\1/p' {} +; git for-each-ref --format='%(refname:strip=3)' refs/sdlc/ids/ | cut -c3-; } | sort -n | tail -1
git update-ref refs/sdlc/ids/T-NNNN "$(printf 'NNNN-<slug>\n' | git hash-object -w --stdin)" ""
mkdir docs/work/NNNN-<slug>
printf '%s\n' --- 'id: T-NNNN' 'title: "<title>"' 'type: feature' 'status: proposed' 'size: L2' 'priority: P2' 'depends: []' 'created: YYYY-MM-DD' 'router: .sdlc/AGENTS.md' --- '' '## Goal' '' '## Acceptance criteria' > docs/work/NNNN-<slug>/handoff.md
```

## Claim

A non-zero exit from the first command means someone holds the ticket (`git cat-file -p refs/sdlc/claims/T-NNNN` names them): pick another one.

```sh
git update-ref refs/sdlc/claims/T-NNNN "$(printf '<by> YYYY-MM-DD\n' | git hash-object -w --stdin)" ""
awk '/^---/{n++} n==1&&/^status:/{$0="status: claimed"} {print} n==1&&/^created:/{print "claimed_by: <by> YYYY-MM-DD"}' docs/work/NNNN-<slug>/handoff.md > handoff.tmp
mv handoff.tmp docs/work/NNNN-<slug>/handoff.md
```

## Release

```sh
awk '/^---/{n++} n==1&&/^claimed_by:/{next} n==1&&/^status:/{$0="status: ready"} {print}' docs/work/NNNN-<slug>/handoff.md > handoff.tmp
mv handoff.tmp docs/work/NNNN-<slug>/handoff.md
git update-ref -d refs/sdlc/claims/T-NNNN
```

## Close

No verifier runs, so the Outcome says `closed by hand (unverified)` and `tickets.py check` warns on it. The last command marks the folder closed: fix any link that cites the old path.

```sh
awk '/^---/{n++} n==1&&/^status:/{$0="status: done"} {print}' docs/work/NNNN-<slug>/handoff.md > handoff.tmp
mv handoff.tmp docs/work/NNNN-<slug>/handoff.md
printf '\n## Outcome\n\nYYYY-MM-DD · lane: hand · verdict: closed by hand (unverified) · verifier: none · base: none\n- Changed: <one line>\n- Commits: see git log\n' >> docs/work/NNNN-<slug>/handoff.md
git update-ref -d refs/sdlc/claims/T-NNNN
mv docs/work/NNNN-<slug> docs/work/.NNNN-<slug>
```

## Documents and rules

- Adding a document: follow `docs/AGENTS.md` "## Adding a document".
- Never push, tag or publish without the user.
- Make worktrees only under `../<repo>.worktrees/`.
- Format only the files you changed, never the whole repository.
- Stop a process by its PID, never by a name pattern (`pkill -f`, `killall`).

Lanes, verification, lint and dispatch need the plugin.
<!-- sdlc:managed:end -->
