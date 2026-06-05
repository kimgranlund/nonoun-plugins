---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Regulation (EU) 2016/679 (GDPR), Article 15 (right of access), Article 17 (right to erasure / 'right to be forgotten'), Article 20 (right to data portability). https://gdpr-info.eu/art-20-gdpr/"
  - "California Consumer Privacy Act / CPRA — consumer rights to know, access, delete, correct, and opt-out. State of California DOJ. https://oag.ca.gov/privacy/ccpa"
  - "Jakob N. \"10 Usability Heuristics for User Interface Design.\" NN/g, 1994 / updated 2024 — esp. Heuristic 3, 'User Control and Freedom' (the 'emergency exit' / undo principle). https://www.nngroup.com/articles/ten-usability-heuristics/"
---

# Auditability & Control

Once a product holds data about a person and acts on their behalf, the question becomes: can the person see, move, correct, undo, and delete what the system holds and does — or are they locked out of their own record? This reference is about that control surface: data access and portability (export), deletion and the account/data lifecycle, audit trails and history, reversibility, and the consolidated "show me everything you know about me" view. It is the operational backstop to `privacy-by-design.md` (which is about not over-collecting in the first place) and `consent-and-permissions.md` (whose "withdraw as easily as you grant" right lives in exactly this control surface). The load-bearing principle: **the user, not just the operator, must have read and write access to their own record** — to inspect it, take a copy, fix it, reverse what the system did, and have it erased. A system the user can only feed and never inspect or unwind is a one-way mirror.

> Two standards anchor this. From data-protection law (GDPR Art. 20), the user has a right to receive their data "in a structured, commonly used and machine-readable format" and to transmit it elsewhere — portability, not just viewing. From usability (Jakob N.'s Heuristic 3, "User Control and Freedom"), users "often perform actions by mistake" and need "a clearly marked 'emergency exit'... support[ing] undo and redo." Control is both a legal entitlement and a usability floor.

The legal scaffolding (GDPR Articles 15/17/20, CCPA/CPRA) is durable and citable; the design patterns that satisfy it (an account dashboard, an export button, an activity log, an undo) are well-established usability practice. This file describes the **design implications** of those rights, not a compliance opinion.

---

## The four data rights, as product surfaces

The convergent core of GDPR and CCPA/CPRA is four rights a user has over the data a product holds. Each maps to a concrete surface the product either ships or doesn't.

| Right | Legal hook | The product surface | Failure mode |
| --- | --- | --- | --- |
| **Access / know** | GDPR Art. 15; CCPA right to know | A view of what's held and why — ideally self-serve, not a request form | "Email us and we'll think about it" / no view at all |
| **Portability / export** | GDPR Art. 20 | A "download my data" in a structured, machine-readable format (JSON/CSV) | A PDF screenshot dump, or no export — data held hostage |
| **Correction** | GDPR Art. 16; CPRA right to correct | A way to fix wrong data the system holds about them | Inaccurate inferences the user can see but can't change |
| **Deletion / erasure** | GDPR Art. 17; CCPA right to delete | A real "delete my account and data," with stated scope and timeline | A "deactivate" that hides but retains; deletion that's actually suspension |

The two most-faked are **portability** and **deletion**. Portability fails when "export" produces a non-machine-readable dump (a PDF, a screenshot) that satisfies the letter and defeats the purpose — the point of Art. 20's "structured, machine-readable format" is that the user can _take their data and leave_, which is precisely what a hostile export prevents. Deletion fails when "delete" silently means "deactivate" — the data persists, and the user has been told a comforting untruth. The honest tell of both: does the user actually end up with their data in a usable form (export), and does the data actually stop existing (deletion)?

---

## "Show me what you know about me"

The strongest version of access is a single, legible view of everything the system holds and infers about the user — not just the data they entered, but the data the system _derived_. Three layers, in rising order of how often they're hidden:

- **What I gave you.** Profile, content, settings — usually visible, the easy part.
- **What you recorded about me.** Activity, history, device and location logs, interaction events — often buried or absent.
- **What you inferred about me.** Derived attributes, interest categories, risk scores, ad-targeting segments — the most consequential and the most commonly hidden. This is where "creepy" lives: the user discovers the system concluded things about them they never stated and can't see.

```text
A real "what you know about me" view exposes all three layers:

  GIVEN     → name, email, the posts I wrote          [usually shown]
  RECORDED  → logins, searches, places, devices         [often hidden]
  INFERRED  → "interested in: hiking, new parent,        [almost always hidden —
               likely income band, churn-risk: low"        and the most sensitive]

  ...each with: why it's held, how long, who else gets it, and a control
     (correct it / delete it / opt out of it).
```

The discipline: inferred data is still the user's data, and the access right covers it. A product that shows what you typed but hides what it concluded has disclosed the trivial layer and withheld the one that actually affects how it treats you.

---

## Audit trails and history

Auditability is the user's ability to see what the _system_ did — a chronological record of actions, especially actions taken on the user's behalf or affecting their account. Distinct from the data view (what's _held_), the audit trail is what _happened_.

- **Account activity log.** Logins, devices, sessions, security events, consent changes — so the user can spot what they didn't do (a sign-in from an unknown device) and revoke it. This is a security control as much as a transparency one.
- **Action history for agentic/automated systems.** When a product acts on the user's behalf (an agent sends, files, buys, edits), it must record what it did, when, and why, in a reviewable log. This is the auditability half of the trust/control discipline in `ai-ux/trust-control-steerability.md`: graded autonomy is only safe if the user can _afterwards_ see and unwind what the system did autonomously.
- **Change history.** For user data the system or others can modify, a history of changes (what changed, when, by whom) makes silent mutation visible and supports recovery.

The tell of good auditability: the user can answer "what happened to my account / my data / on my behalf, and when?" from a log they can actually reach. The tell of bad: actions happen invisibly, and the user reconstructs them only from their consequences.

---

## Reversibility — undo over confirm

Control is hollow if the user can see what happened but can't unwind it. Jakob N.'s third heuristic, "User Control and Freedom," is the principle: because "users often perform actions by mistake," the system needs "a clearly marked 'emergency exit'" and should "support undo and redo." The design hierarchy, strongest to weakest:

1. **Undo.** The action happens immediately and is fully reversible afterward (sent → "Undo send"; deleted → restorable from trash for N days). This is the gold standard: it keeps the product fast _and_ safe, and it beats a confirmation dialog because it doesn't interrupt the common case.
2. **Reversible-by-design.** The action is non-destructive (archive instead of delete; draft instead of publish), so "undo" is just doing the inverse.
3. **Confirmation.** A pre-action "are you sure?" — the weakest control, because users learn to click through it. Reserve confirmation for the genuinely irreversible; don't substitute it for undo on things that could simply be reversible.

The relationship to risk: reversibility is what _lets_ a system act with low friction. An action that can be undone can run with a light touch; an action that cannot must drop to high friction or human confirmation (this is the risk × reversibility calibration in `ai-ux/trust-control-steerability.md`, and the friction-as-safety discipline in `risk-and-harm-handling.md`). Designing for reversibility first means most actions never need a heavy gate at all.

---

## Account and data lifecycle

Control extends across the whole life of the account, not just its active use. The lifecycle has stages the product must handle honestly:

- **Active.** Data in use, bound to purpose (per `privacy-by-design.md`'s minimization).
- **Dormant / deactivated.** The user steps away. Be honest about the distinction: _deactivation_ (recoverable, data retained) and _deletion_ (permanent, data destroyed) are different promises — conflating them, so "delete" really means "hide," is a dark pattern.
- **Deletion.** A real path to permanent erasure, with stated scope (what's deleted, what's legally retained and why — e.g. transaction records law requires keeping), a timeline (GDPR's "without undue delay"), and propagation to backups and third parties the data was shared with. Deletion that doesn't reach the copies isn't deletion.
- **Export-before-delete.** The humane lifecycle lets the user take their data (portability) on the way out — leaving with a usable copy, not being held by the inconvenience of starting over elsewhere. (Lock-in by non-portability is the retention dark pattern this prevents.)

The tell of an honest lifecycle: "delete" deletes (with a clear, lawful exception list), and the user can leave with their data. The tell of a hostile one: "delete" suspends, export is a PDF, and the only real way out is abandonment.

---

## Anti-patterns

- **The one-way mirror.** The user can feed the system but never inspect what it holds or infers — no access view, especially of derived data.
- **Hostage export.** "Download my data" yields a PDF or screenshot, not a machine-readable file — satisfies the letter of portability, defeats its purpose (leaving).
- **Deletion that's deactivation.** "Delete my account" silently retains the data; the user is told a comforting untruth (a dark pattern, and a GDPR Art. 17 failure).
- **Inferred-data blackout.** What the user typed is visible; what the system concluded about them is hidden — the consequential layer withheld.
- **Invisible action.** A system (especially an agent) acts on the user's behalf with no reviewable log — the user reconstructs events from their damage.
- **Confirm instead of undo.** A wall of "are you sure?" dialogs the user clicks through, where reversible-by-design or undo would actually protect them (Jakob N. H3).
- **Unreachable rights.** Access/export/delete exist only as an email-the-company process with no timeline — present on paper, useless in practice.

---

## The scoring test: can the user inspect, move, undo, and erase?

1. **Access — including inferred.** Can the user see what's held _and what the system inferred_ about them, with why/how-long/who-else — or only the data they typed?
2. **Portable.** Is there an export in a structured, machine-readable format the user can actually take elsewhere (GDPR Art. 20) — or a hostage PDF / no export?
3. **Auditable.** Can the user see what happened to their account and what the system did on their behalf, from a reachable log — or only infer it from consequences?
4. **Reversible.** Does the product favor undo and reversible-by-design over click-through confirmations, and reach for confirmation only on the genuinely irreversible (Jakob N. H3)?
5. **Honest lifecycle.** Does "delete" actually erase (with a clear lawful-retention exception list and propagation to copies), and can the user leave with their data — or does "delete" mean "hide"?

A product passes when a user can open one place, see everything the system holds and concluded about them, take a usable copy, fix what's wrong, review and unwind what the system did, and truly delete it all when they leave. It fails when the user is locked inside their own record — able to add but not inspect, to leave but not take their data, to "delete" without anything being deleted.

---

## One labeled caveat

This file describes **design implications, not legal advice or a compliance opinion**. The GDPR rights are Articles 15 (access), 16 (rectification), 17 (erasure), and 20 (portability, incl. the verbatim "structured, commonly used and machine-readable format"); the CCPA/CPRA rights to know, delete, correct, and opt-out track the California DOJ overview. Specific timelines (GDPR's "without undue delay" / one month; CCPA's 45 days) and lawful-retention exceptions vary by jurisdiction and data type — treat the _rights_ as durable and verify current statutory detail before relying on a number. "User Control and Freedom" (undo/redo, "emergency exit") is Jakob N.'s Heuristic 3 (NN/g, 1994 / updated 2024). The autonomy-logging and risk × reversibility connections are developed in `ai-ux/trust-control-steerability.md`; friction-as-safety in `risk-and-harm-handling.md`.
