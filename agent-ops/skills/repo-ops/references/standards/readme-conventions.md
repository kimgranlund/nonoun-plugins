---
date: 2026-04-27
coverage: canonical
peers:
  - agents-md-spec.md
  - claude-md-convention.md
  - cross-tool-matrix.md
  - ../audit-patterns/redundancy-detection.md
primary_sources:
  - https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-health-files
  - https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository
  - https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors
  - https://opensource.guide/code-of-conduct/
  - https://www.contributor-covenant.org/
  - https://keepachangelog.com/
status: research-verified
---

# README, CONTRIBUTING, SECURITY — the human-and-LLM landing files

> **The premise.** AGENTS.md is for agents only. README.md is the _front door_ — where humans land first, where GitHub auto-renders, where the LLM lands when the user pastes a repo URL into a chat. The two files have different jobs and shouldn't duplicate each other.

## The role split

| File | Audience | Role | Loaded by agent? |
| --- | --- | --- | --- |
| `README.md` | Humans + LLMs in cold-start | What this project is, install + run, how to find more | Often (when user references the repo at large) |
| `AGENTS.md` | Coding agents in a session | How to _work in_ this repo: commands, conventions, trust boundaries, memory homes | Always (every session) |
| `CONTRIBUTING.md` | Humans contributing | How to participate: PR process, code review norms, contributor onboarding | Sometimes |
| `SECURITY.md` | Humans + automated scanners | How to report vulnerabilities; supported versions; disclosure policy | Rarely |
| `CODE_OF_CONDUCT.md` | Contributors + maintainers | Behavior expectations | Almost never |

README.md and AGENTS.md are **complementary, not redundant**. The redundancy-detection pattern (`../audit-patterns/redundancy-detection.md`) catches when build commands or facts appear in both — that's where drift starts.

## README.md — the human + LLM front door

| Section | Required? | Notes |
| --- | --- | --- |
| Project name + tagline | Yes | One sentence |
| What it does | Yes | One paragraph |
| Why use it (over alternatives) | Recommended | If applicable |
| Quickstart / install | Yes | Minimal commands; link to AGENTS.md for full setup |
| Usage example | Recommended | Smallest meaningful example |
| Documentation pointer | Yes | Link to `docs/`, AGENTS.md, or external docs site |
| License | Yes | Or link to `LICENSE` |
| Contributing pointer | Recommended | One line linking to `CONTRIBUTING.md` |
| Security pointer | Recommended | One line linking to `SECURITY.md` |
| Status badges | Optional | Don't bloat — pick load-bearing 2-3 |

### What does NOT go in

- **Full build/test/run commands** — that's AGENTS.md's job. README has a _quickstart_; AGENTS.md has the canonical commands. Both = drift waiting to happen.
- **Conventions / coding standards** — AGENTS.md or CONTRIBUTING.md.
- **Architecture details** — `ARCHITECTURE.md`.
- **Trust boundaries / agent-specific instructions** — AGENTS.md.
- **Long FAQ** — `docs/faq.md`.

### Length target

200-300 lines for open-source. Internal/private repos: 50-150. A 1000-line README is almost always content that belongs in `docs/`.

### Pointer-discipline pattern

The README's job is to _route_ — not _contain_.

````markdown
# Acme Service

A high-throughput message router for federated agent systems.

## Quickstart

```bash
pnpm install
pnpm dev
```

For canonical build / test / run commands and contributor conventions, see [AGENTS.md](./AGENTS.md). For full architecture, see [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Documentation

- **For agents (Claude, Codex, Cursor, ...):** [`AGENTS.md`](./AGENTS.md)
- **Contributing:** [`CONTRIBUTING.md`](./CONTRIBUTING.md)
- **Security policy:** [`SECURITY.md`](./SECURITY.md)
- **Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **Decisions (ADRs):** [`.agents/brain/adrs/`](.agents/brain/adrs/)

## License

[Apache 2.0](LICENSE).

_Last reviewed: 2026-04-27_

````

The `pnpm dev` command in the quickstart is duplicated minimally on purpose — humans skim README and want "can I run this in 30 seconds?". The agent reaches for AGENTS.md anyway.

## CONTRIBUTING.md — how humans participate

GitHub auto-renders `CONTRIBUTING.md` and surfaces it in the contributor flow (per [GitHub's community-health docs](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions)).

| Section | Required? | Notes |
| --- | --- | --- |
| Local setup | Yes | Or link to AGENTS.md / `docs/setup.md` |
| Running tests | Yes | Or link to AGENTS.md |
| Branching / commit conventions | Yes | E.g., Conventional Commits |
| PR process | Yes | Where to open PRs, who reviews, expected turnaround |
| Code-review norms | Recommended | E.g., "approve on intent, not nitpicks" |
| Issue templates / labels | Recommended | If you use them |
| Code of conduct + Security pointers | Recommended | One-line links |

### CONTRIBUTING vs AGENTS — the key split

CONTRIBUTING is for **humans contributing** (norms, review process, branching). AGENTS is for **agents working in the repo** (commands, conventions, trust boundaries). They overlap on `Build / test / run`, and that's where drift happens. Cleanest pattern:

```markdown
## Local setup
For build / test / run commands, see [`AGENTS.md`](./AGENTS.md). For
contribution conventions specific to humans (branching, PR flow,
code-review norms), continue below.
```

Same redundancy-elimination pattern as `../audit-patterns/redundancy-detection.md`.

## SECURITY.md — disclosure policy

GitHub auto-renders `SECURITY.md` at `<repo>/security/policy` and links to it from the **Report a vulnerability** flow (per [GitHub's adding-a-security-policy docs](https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository)).

```markdown
# Security Policy

## Supported versions

| Version | Supported          |
|---------|--------------------|
| 2.x     | :white_check_mark: |
| 1.x     | :x:                |

## Reporting a vulnerability

Please report vulnerabilities to security@acme.example. We respond
within 48 hours. Do **not** file public issues for security reports.

We follow [coordinated vulnerability disclosure](https://www.cisa.gov/coordinated-vulnerability-disclosure-process):
acknowledge within 48h, investigate within 7d, public disclosure
within 90 days of report (or upon fix release, whichever sooner).

_Last reviewed: 2026-04-27_
```

### `SECURITY.md` placement

Three locations are equally valid (per GitHub docs):

| Location | When |
| --- | --- |
| `SECURITY.md` (repo root) | Most repos |
| `.github/SECURITY.md` | If you keep policy files in `.github/` |
| `docs/SECURITY.md` | If you want it docs-aligned (renders in GitHub UI either way) |

GitHub auto-renders all three. **Pick one — having two is confusing.**

What does NOT go in: implementation details of past vulnerabilities (those go in `.agents/brain/postmortems/` with sensitive details redacted), threat-model docs (`docs/threat-model.md`), compliance attestations (`docs/compliance/`).

## CODE_OF_CONDUCT.md — behavior expectations

Most projects use the [Contributor Covenant](https://www.contributor-covenant.org/) verbatim — the de facto industry default. Placement: repo root or `.github/`. Same auto-render rules as SECURITY.md. The audit flags absence on public/community repos as **recommended-low**; for internal-only repos, not required.

## How AGENTS.md should reference these files

In `Where to find things`:

```markdown
- **README:** `README.md` — the human-and-LLM front door
- **Contributor guide:** `CONTRIBUTING.md`
- **Security policy:** `SECURITY.md`
- **Code of conduct:** `CODE_OF_CONDUCT.md`
```

These are _navigation_ references. The agent already loads AGENTS.md every session; it pulls in README/CONTRIBUTING/SECURITY only when the user's question implies it.

## Avoiding redundancy with AGENTS.md

| Topic | AGENTS.md | README.md | CONTRIBUTING.md | SECURITY.md |
| --- | --- | --- | --- | --- |
| What this project is | brief tagline (header) | full one-paragraph | (no) | (no) |
| Build / test / run | **canonical** | quickstart only, link to AGENTS | "see AGENTS.md" | (no) |
| Conventions | **canonical** | (no) | branching/commits only | (no) |
| Trust boundaries | **canonical** | (no) | (no) | (no) |
| Where to find things | **canonical** | brief pointer to AGENTS | (no) | (no) |
| Memory primitives | **canonical** | (no) | (no) | (no) |
| PR process | (no) | (no) | **canonical** | (no) |
| Vulnerability reporting | (no) | (no) | (no) | **canonical** |
| Architecture | "see ARCHITECTURE.md" | "see ARCHITECTURE.md" | (no) | (no) |

Every cell with **canonical** is the _only_ place that information lives. Other cells link to it. Detected/enforced by `../audit-patterns/redundancy-detection.md`.

## GitHub UI behaviors

- README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT all get **auto-rendered** at well-known URLs.
- The **community profile** view (`<repo>/community`) shows which recommended files are present.
- The "first-time contributor" prompt surfaces CONTRIBUTING and CODE_OF_CONDUCT.
- The **Report a vulnerability** flow surfaces SECURITY.md.
- GitHub does **not** auto-render AGENTS.md as anything special — it's just Markdown. The `agents.md` standard exists to be agent-readable, not GitHub-UI-special.

## Audit checks

1. `README.md` exists, ≤300 lines (warn at 200; error at 500).
2. `CONTRIBUTING.md` exists for public/community repos.
3. `SECURITY.md` exists for public/community repos with users.
4. `CODE_OF_CONDUCT.md` exists for public/community repos with contributors.
5. None duplicate AGENTS.md's canonical content (build commands, conventions, trust boundaries) — flag as drift risk per `../audit-patterns/redundancy-detection.md`.
6. README references AGENTS.md (so agents and humans converge on the same canonical instructions).
7. SECURITY.md is in _one_ location (root, `.github/`, or `docs/`) — flag if multiple.

## Common anti-patterns

- **README.md duplicates the entire AGENTS.md.** Drift waiting to happen. Compress to a routing layer.
- **CONTRIBUTING.md re-lists build commands.** Same drift problem. Link to AGENTS.md.
- **SECURITY.md says "report vulnerabilities" without saying _how_.** Useless. Include contact + SLA.
- **CODE_OF_CONDUCT.md modified beyond the Contributor Covenant baseline.** Usually unproductive scope creep.
- **Status badges everywhere, no real content.** Fails the "what does this do?" test in 5 seconds.
- **README.md without `_Last reviewed:_` or frontmatter date.** Fails the staleness gate.

## Cross-references

- AGENTS.md spec: `agents-md-spec.md`
- CLAUDE.md as thin pointer: `claude-md-convention.md`
- Cross-tool compatibility matrix: `cross-tool-matrix.md`
- Redundancy detection: `../audit-patterns/redundancy-detection.md`
- Greenfield setup: `../recipes/greenfield-setup.md`
