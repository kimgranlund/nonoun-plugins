# Host adapter: Claude Code

Load when a route fails although the corpus is sound, when deciding where a rule must live so that this host
delivers it, or before a fresh-agent trial on this host. The routing core stays host-neutral
([tier model](../tier-model.md#shared-machinery-where-applicable)); everything specific to one harness is here.

**Dated.** Documentation read 2026-11-13 at `https://code.claude.com/docs/en/` (pages named per row). Probed the
same day on Claude Code 2.1.325, non-interactive runs and delegated agents, with a marker sentence planted in each
surface and one planted where nothing loads it (never seen: the control). Compaction was not probed, so the
"After compaction" column is documentation only. A row is as good as its date: re-run the [probe](#probe) after a
host upgrade and before relying on a row for a repair.

Contents: [Surfaces](#surfaces) · [What a fresh agent receives](#what-a-fresh-agent-receives) · [Failures the corpus cannot see](#failures-the-corpus-cannot-see) · [Probe](#probe)

## Surfaces

"Advisory" means the model reads it and may still act otherwise; "enforced" means the host acts whatever the model
decides. "Kept" is what the documentation says holds after the conversation is compacted.

| Surface | Loads when | Written by | Advisory or enforced | After compaction | Observe with | Documented (page) | Probed |
|---|---|---|---|---|---|---|---|
| System prompt, output style | Session start; a style replaces part of the prompt | The host; the user for a style or an appended prompt | Advisory, highest position | Kept | Not shown; ask the agent | `output-styles`, `cli-reference` | Not probed |
| Entry file at or above the start directory (`CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`) | Session start, as a message after the system prompt, root-most first | The project; the person for the local file | Advisory | Re-read from disk | `/memory`, `/context`, an `InstructionsLoaded` hook | `memory` | Match: loaded at start, also from a parent directory |
| `AGENTS.md` | Session start, only when no `CLAUDE.md` or `CLAUDE.local.md` exists at or above the start directory (default setting) | The project | Advisory | Not stated | `/memory`; no `InstructionsLoaded` event | `memory` | Match: loaded alone; **not loaded** once a `CLAUDE.local.md` was added |
| `@path` import in an entry file | With the importing file, at most four hops deep; an import that resolves outside the start directory needs a one-time approval | The project | Advisory | With its importer | `InstructionsLoaded`, reason `include` | `memory` | Match: hops 1 to 4 loaded, hop 5 not. From a subdirectory start in a non-interactive run, the parent entry loaded and its imports did not |
| Rule file without `paths` (`.claude/rules/`) | Session start | The project or the person | Advisory | Re-read from disk | `InstructionsLoaded`, reason `session_start` | `memory` | Match |
| Rule file with `paths` | When a matching file is read, written or edited | The project | Advisory | Dropped until a matching file is touched again | `InstructionsLoaded`, reason `path_glob_match` | `memory`, `context-window` | Match: absent at start, arrived beside the first read |
| Entry file in a subdirectory | When a file in that directory is read, written or edited | The project | Advisory | Dropped until the directory is touched again | `InstructionsLoaded`, reason `nested_traversal` | `memory`, `context-window` | Match: absent at start; arrived beside the first read, and only after a first write |
| Auto memory (`MEMORY.md` index) | Session start, first 200 lines or 25 KB; topic files on demand | The agent | Advisory | Re-read from disk | `/memory` | `memory` | Not probed (none existed) |
| Skill listing (name and description) | Session start; descriptions are dropped, least-used first, when the listing passes its budget (1% of the context window); each description cut at 1,536 characters | Skill authors | Advisory; it is the skill's only route | Rebuilt | `/skills`, `/context`, `/doctor` | `skills` | Match: a planted description arrived whole; in a session with 100 skills listed, 47 arrived as a name only |
| Skill body | On invocation, as one message; not re-read later | Skill author | Advisory | First 5,000 tokens per skill, 25,000 in all, newest first | The transcript | `skills`, `context-window` | Match: body absent until invoked |
| Skills, entry files and rules in a subdirectory project | When a file there is first read | The project | Advisory | As their own rows | The listing grows mid-session | `skills`, `memory` | Match: one read brought the nested entry, its imports, its rules and its skill |
| Custom command (`.claude/commands/`) | As a skill | The project or the person | Advisory | As a skill | `/skills` | `skills`, `commands` | Not probed |
| Agent definition: description | Session start, in the delegating agent's list | Agent author | Advisory | Not stated | The agent list | `sub-agents` | Match |
| Agent definition: body | Becomes the delegated agent's system prompt | Agent author | Advisory | Belongs to the delegated agent | Ask the delegated agent | `sub-agents` | Match |
| Hook | At its lifecycle event; a `PreToolUse` hook can deny the call in every permission mode | The project, the person or the organization | **Enforced** | Unaffected (configuration, not context); text a hook added earlier is summarized | `/hooks`, debug log | `hooks`, `hooks-guide` | Match: the same request changed the file without the hook and was refused with it |
| Permission rule, settings | Session start; deny before ask before allow; organization settings outrank the rest | The person, the project, the organization | **Enforced** | Unaffected | `/permissions`, `/status` | `permissions`, `settings` | Not probed |
| MCP server instructions, tool names | Session start; tool definitions are deferred until searched for; instructions cut at 4,096 characters | The server's author | Advisory | Not stated | `/mcp`, `/context` | `mcp` | Seen in a delegated agent's context; limits not probed |
| Tool result | When the tool returns; MCP output is limited (25,000 tokens by default) | The tool, and whatever it read | Data, not instruction | Summarized; up to five recent files re-read | The transcript | `mcp`, `context-window` | A marker in a read file arrived in the result; limits not probed |

## What a fresh agent receives

A delegated agent starts with its own system prompt and the task message. It never receives the delegating
conversation, the files already read, or the skill bodies already loaded. Beyond that the kind of agent decides:

| Kind | Entry files and unscoped rules | Skill listing | Subdirectory entries and scoped rules | Probed |
|---|---|---|---|---|
| General-purpose | Yes | Yes, with descriptions | On first read there | Match |
| Custom, from a definition | Yes, unless the definition opts out | Not in the probed agent (its tools were limited to reading) | On first read there | Match |
| Built-in research and planning agents | **No** | Yes | On first read there | Match: saw neither the root entry nor an unscoped rule |
| A fork | Inherits the whole conversation: not a fresh agent | | | Not probed |

The delegating agent's auto memory and output style are documented as not reaching a non-fork agent.

## Failures the corpus cannot see

Each passes every static check, because the corpus is not what is wrong.

- **The entry is not the file the host loads.** A corpus whose entry is `AGENTS.md` routes correctly alone; add an
  uncommitted `CLAUDE.local.md` and the host stops loading the entry (documented also for a `CLAUDE.md` in any
  directory above). Probed with one task and one frozen acceptance: passed alone, failed with the local file added,
  passed again with a one-line `CLAUDE.md` that imports the entry. Repair: the host file imports the canonical entry.
- **The rule lives where the host loads late.** A subdirectory entry or a scoped rule arrives beside the first read
  in its scope, so a task that writes a new file there first acts before the rule arrives (probed: both arrived only
  after the write), and after compaction the rule is gone until the scope is touched again (documented). Repair: the root entry routes to the contract with a load condition;
  the late surface may repeat nothing the route does not already reach.
- **The agent was started without the entry.** A research or planning agent, or one whose definition opts out,
  begins from the task message alone. Repair: the brief names the entry path.
- **The import is one hop too deep, or outside the start directory.** It is silently not expanded. Repair: flatten,
  or link with a load condition.
- **The skill is listed by name only.** It cannot be chosen from a description the host dropped. Repair: fewer or
  shorter descriptions, key use first; check the listing the agent actually received.

## Probe

1. In a scratch copy of the corpus, add one marker sentence (a made-up token) to each surface under test and one to
   a file nothing loads.
2. Add an `InstructionsLoaded` hook to the scratch copy's own settings that appends each event's `file_path`,
   `load_reason` and `trigger_file_path` to a log: this is the host's own account of what it loaded and why.
3. Start a fresh non-interactive session with no file tools and ask which markers are in context; then allow one
   read in a subdirectory and ask again. Repeat through each kind of delegated agent in use.
4. A row holds when the log and the answer agree with it and the unloaded marker is never reported. Record the host
   version and date with the result; these are evaluator-directed runtime probes
   ([evidence levels](../evaluation.md#evidence-levels)), not proof of what a model retained.
