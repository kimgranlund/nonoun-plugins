# Crawl milestone — the answer key

`replay.py` is the **Crawl-phase milestone** (TDD §19): one cell driven `absent → defined → validated`
*entirely through the server API* (`api.py`), the full engine define→create→validate as a sequence of
tickets, with no heartbeat, no UI, and no auto-dispatch — a human drives it. Where the kernel's
`tracer-bullet` proves the morphism on the validate step in isolation, this proves the whole coordination
path works end-to-end through the single-writer server, and that **each phase earns the next** (Walk's
heartbeat is unlocked only once Crawl is mechanically met).

Answer key (kept outside the fixture so a cold judge run stays honest):

| Check | Claim |
|---|---|
| **M1** | the cell traverses `absent → defined → instantiated → validated`, every transition applied by the server (single-writer); both tickets reach `done`. |
| **M2** | the **authoring** advances (`absent→defined`, `defined→instantiated`) need *no* critic signal — the worker wrote the asset, the server records the bump; the **validated** advance *does* require one. The trust line sits exactly at `validated`. |
| **M3** | a worker can forge **neither** the signal (`gate-signal` exit 2) **nor** the maturity (`gate-verifier` denies writing `lattice.json`). Maturity is server-only. |
| **M4** | a real signal file is on disk (the forged one never landed); the lattice grid (the SQLite index) shows the cell `validated`; the append-only ledger holds the full arc — the authoring transitions, the critic's pass signal, and the validated transition. |

## The engine shape it exercises

A ticket targets one **legal single edge** of the maturity machine (`absent→defined`, `defined→instantiated`,
`instantiated→validated`). The arc `absent→validated` is therefore three tickets: **define** and **create**
are authoring advances (server-applied, no signal); **validate** is the signal-bearing advance that runs the
validation path and is gated by `gate-signal`. The bootstrapping rubric is seeded `validated` (a kit's job);
the milestone assumes a validated verifier exists, exactly as a real cold start would have one.

## Run it

```bash
python3 dev-factory/dev-server/evals/crawl-milestone/replay.py   # exit 0 = Crawl met
```

Stdlib + `sqlite3` only — no FastAPI needed (the milestone exercises `api.py`, the tested operations layer;
`app.py` is only the HTTP transport over it).
