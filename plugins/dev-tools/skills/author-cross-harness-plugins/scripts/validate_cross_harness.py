#!/usr/bin/env python3
"""Validate structural and semantic portability between Claude Code and Codex plugins."""

from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TOP_LEVEL_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")
CLAUDE_TOKEN_RE = re.compile(r"\$\{CLAUDE_[A-Z0-9_]+\}|\$ARGUMENTS")
CLAUDE_ONLY_SKILL_FIELDS = {
    "argument-hint",
    "arguments",
    "disable-model-invocation",
    "user-invocable",
    "disallowed-tools",
    "model",
    "effort",
    "context",
    "agent",
    "hooks",
    "paths",
    "shell",
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def read_json(path: Path, report: Report) -> dict[str, Any] | None:
    if not path.is_file():
        report.error(f"missing required file: {path}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.error(f"invalid JSON: {path}: {exc}")
        return None
    if not isinstance(data, dict):
        report.error(f"expected a JSON object: {path}")
        return None
    return data


def parse_frontmatter(path: Path, report: Report) -> tuple[dict[str, Any], str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        report.error(f"cannot read {path}: {exc}")
        return {}, ""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        report.error(f"missing YAML frontmatter: {path}")
        return {}, text
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        report.error(f"unterminated YAML frontmatter: {path}")
        return {}, text

    meta: dict[str, Any] = {}
    front = lines[1:end]
    i = 0
    while i < len(front):
        line = front[i]
        match = TOP_LEVEL_KEY_RE.match(line)
        if not match:
            i += 1
            continue
        key, raw = match.group(1), (match.group(2) or "").strip()
        if raw in {">", ">-", "|", "|-"}:
            parts: list[str] = []
            i += 1
            while i < len(front) and (not front[i].strip() or front[i].startswith((" ", "\t"))):
                if front[i].strip():
                    parts.append(front[i].strip())
                i += 1
            meta[key] = " ".join(parts)
            continue
        if raw.lower() in {"true", "false"}:
            meta[key] = raw.lower() == "true"
        else:
            meta[key] = raw.strip("\"'")
        i += 1
    return meta, "\n".join(lines[end + 1 :]).lstrip("\n")


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text.strip()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1 :]).strip()
    return text.strip()


def manifest_path(root: Path, manifest: dict[str, Any], key: str) -> Path | None:
    value = manifest.get(key)
    if isinstance(value, list):
        value = value[0] if value else None
    if not isinstance(value, str):
        return None
    return root / value.removeprefix("./")


def check_manifest_pair(
    root: Path, claude: dict[str, Any] | None, codex: dict[str, Any] | None, report: Report
) -> None:
    if claude is None or codex is None:
        return
    for key in ("name", "version", "description"):
        if claude.get(key) != codex.get(key):
            report.error(
                f"manifest identity mismatch for {key!r}: "
                f"Claude={claude.get(key)!r}, Codex={codex.get(key)!r}"
            )
    name = claude.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        report.error(f"plugin name must be lowercase hyphen-case: {name!r}")
    if "hooks" in codex:
        report.error(
            "Codex manifest must omit unsupported 'hooks'; keep root hooks.json for convention discovery"
        )

    for label, manifest in (("Claude", claude), ("Codex", codex)):
        skills = manifest_path(root, manifest, "skills") or root / "skills"
        if not skills.is_dir():
            report.error(f"{label} skills path does not exist: {skills}")
        for key in ("hooks", "mcpServers", "agents", "commands"):
            path = manifest_path(root, manifest, key)
            if path is not None and not path.exists():
                report.error(f"{label} manifest {key} path does not exist: {path}")


def bool_in_openai_yaml(path: Path, key: str) -> bool | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^\s*{re.escape(key)}:\s*(true|false)\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not match:
        return None
    return match.group(1).lower() == "true"


def scan_portability_tokens(path: Path, text: str, report: Report) -> None:
    for match in CLAUDE_TOKEN_RE.finditer(text):
        report.error(f"Claude-only token {match.group(0)!r} in shared file: {path}")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("!`"):
            report.error(f"Claude dynamic command injection in shared file: {path}:{lineno}")


def check_skill_resources(shared: Path, adapter: Path, report: Report) -> None:
    ignored = {Path("SKILL.md"), Path("agents/openai.yaml")}
    shared_files = {
        path.relative_to(shared)
        for path in shared.rglob("*")
        if path.is_file() and path.relative_to(shared) not in ignored
    }
    adapter_files = {
        path.relative_to(adapter)
        for path in adapter.rglob("*")
        if path.is_file() and path.relative_to(adapter) not in ignored
    }
    for relative in sorted(shared_files - adapter_files):
        report.error(f"Claude skill adapter is missing shared resource: {adapter / relative}")
    for relative in sorted(adapter_files - shared_files):
        report.error(f"orphan resource in Claude skill adapter: {adapter / relative}")
    for relative in sorted(shared_files & adapter_files):
        if (shared / relative).read_bytes() != (adapter / relative).read_bytes():
            report.error(f"Claude skill adapter resource drift: {adapter / relative}")


def check_skills(root: Path, claude: dict[str, Any] | None, codex: dict[str, Any] | None, report: Report) -> None:
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return
    claude_skills = manifest_path(root, claude or {}, "skills") or skills_dir
    codex_skills = manifest_path(root, codex or {}, "skills") or skills_dir
    if codex_skills != skills_dir:
        report.error(f"Codex manifest must point at the strict shared skill tree: {skills_dir}")
    using_claude_adapter = claude_skills != skills_dir

    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            report.error(f"skill directory has no SKILL.md: {skill_dir}")
            continue
        meta, body = parse_frontmatter(skill_file, report)
        name = meta.get("name")
        description = meta.get("description")
        if name != skill_dir.name:
            report.error(f"skill name {name!r} does not match directory {skill_dir.name!r}")
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            report.error(f"invalid skill name in {skill_file}: {name!r}")
        if not isinstance(description, str) or not description.strip():
            report.error(f"missing skill description: {skill_file}")
        elif len(description) > 1024:
            report.error(f"skill description exceeds 1024 characters: {skill_file}")

        forbidden = sorted(CLAUDE_ONLY_SKILL_FIELDS.intersection(meta))
        if forbidden and using_claude_adapter:
            report.error(
                f"Claude-only frontmatter in strict shared skill {skill_file}: "
                + ", ".join(forbidden)
            )

        scan_portability_tokens(skill_file, body, report)
        implicit = bool_in_openai_yaml(skill_dir / "agents" / "openai.yaml", "allow_implicit_invocation")
        if using_claude_adapter:
            adapter_dir = claude_skills / skill_dir.name
            adapter_file = adapter_dir / "SKILL.md"
            if not adapter_file.is_file():
                report.error(f"missing Claude skill adapter: {adapter_file}")
                continue
            adapter_meta, adapter_body = parse_frontmatter(adapter_file, report)
            if adapter_meta.get("name") != name:
                report.error(f"Claude skill adapter name differs: {adapter_file}")
            if adapter_meta.get("description") != description:
                report.error(f"Claude skill adapter description differs: {adapter_file}")
            if strip_frontmatter(body) != strip_frontmatter(adapter_body):
                report.error(f"Claude skill adapter body drift: {adapter_file}")
            check_skill_resources(skill_dir, adapter_dir, report)

            human_only = adapter_meta.get("disable-model-invocation") is True
            if human_only and implicit is not False:
                report.error(
                    f"{skill_dir.name}: Claude is human-only but Codex "
                    "agents/openai.yaml does not set allow_implicit_invocation: false"
                )
            if not human_only and implicit is False:
                report.error(
                    f"{skill_dir.name}: Codex is explicit-only while Claude permits model invocation"
                )
            if adapter_meta.get("user-invocable") is False:
                report.warn(
                    f"{skill_dir.name}: Claude model-only visibility has no exact Codex equivalent; "
                    "record the explicit-invocation fallback in HARNESS-NOTES.md"
                )
            if adapter_meta.get("context") == "fork" or adapter_meta.get("agent"):
                report.warn(
                    f"{skill_dir.name}: Claude fork/agent execution needs an inline or "
                    "native-delegation fallback documented in HARNESS-NOTES.md"
                )
        else:
            # Claude-native tree (adia adr-0006): skills/ is the Claude tree, so the
            # Claude-only invocation keys live in the shared SKILL.md and Codex reads
            # them through agents/openai.yaml; no adapter twin exists to compare.
            human_only = meta.get("disable-model-invocation") is True
            if human_only and implicit is not False:
                report.error(
                    f"{skill_dir.name}: Claude is human-only but Codex "
                    "agents/openai.yaml does not set allow_implicit_invocation: false"
                )
            if not human_only and implicit is False:
                report.error(
                    f"{skill_dir.name}: Codex is explicit-only while Claude permits model invocation"
                )
            if meta.get("user-invocable") is False:
                report.warn(
                    f"{skill_dir.name}: Claude model-only visibility has no exact Codex equivalent; "
                    "record the explicit-invocation fallback in HARNESS-NOTES.md"
                )

    if using_claude_adapter and claude_skills.is_dir():
        for adapter_dir in sorted(p for p in claude_skills.iterdir() if p.is_dir()):
            if not (skills_dir / adapter_dir.name / "SKILL.md").is_file():
                report.error(f"orphan Claude skill adapter: {adapter_dir}")


def compare_adapter_pair(shared: Path, adapter: Path, label: str, report: Report) -> None:
    try:
        shared_body = strip_frontmatter(shared.read_text(encoding="utf-8"))
        adapter_body = strip_frontmatter(adapter.read_text(encoding="utf-8"))
    except OSError as exc:
        report.error(f"cannot compare {label} adapter: {exc}")
        return
    if shared_body != adapter_body:
        report.error(f"{label} adapter body drift: {adapter} differs from {shared}")


def _has_claude_frontmatter(path: Path) -> bool:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            return False
        if TOP_LEVEL_KEY_RE.match(line) and TOP_LEVEL_KEY_RE.match(line).group(1) == "name":
            return True
    return False


def check_agents_and_commands(root: Path, claude: dict[str, Any] | None, report: Report) -> None:
    agent_dir = root / "agents"
    claude_agents = root / "adapters" / "claude" / "agents"
    root_agents = sorted(agent_dir.glob("*.md")) if agent_dir.is_dir() else []
    if claude_agents.is_dir():
        # Claude Code has no manifest field for relocating agents (verified, CLI 2.1.250:
        # an "agents" key in plugin.json is rejected outright) — it only ever discovers
        # agents from the plugin's own root agents/ directory. This tree can never be read.
        report.error(
            f"{claude_agents} exists but Claude Code has no manifest field to relocate "
            "agents — it only discovers them from the plugin's root agents/ directory. "
            "Put Claude frontmatter directly on the root agents/<name>.md file instead "
            "and delete this tree (see claude-code.md's Agent adapter section)."
        )
    elif root_agents:
        unframed = [a for a in root_agents if not _has_claude_frontmatter(a)]
        if unframed:
            names = ", ".join(a.name for a in unframed)
            report.warn(
                "Codex agents exist without Claude frontmatter on the same root file "
                f"({names}); Claude will lack deliberate agent routing metadata for these"
            )

    commands = root / "commands"
    claude_commands = root / "adapters" / "claude" / "commands"
    root_commands = sorted(commands.glob("*.md")) if commands.is_dir() else []
    for command in root_commands:
        scan_portability_tokens(command, strip_frontmatter(command.read_text(encoding="utf-8")), report)
    if root_commands and claude_commands.is_dir():
        configured = manifest_path(root, claude or {}, "commands")
        if configured != claude_commands:
            report.error(
                "Claude command adapters exist but the Claude manifest does not point "
                f"commands at {claude_commands}"
            )
        for shared in root_commands:
            adapter = claude_commands / shared.name
            if not adapter.is_file():
                report.error(f"missing Claude command adapter for {shared.name}")
            else:
                compare_adapter_pair(shared, adapter, "command", report)


def hook_signature(data: dict[str, Any]) -> set[tuple[str, str, str]]:
    result: set[tuple[str, str, str]] = set()
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return result
    for event, entries in hooks.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            matcher = str(entry.get("matcher", ""))
            actions = entry.get("hooks")
            if not isinstance(actions, list):
                continue
            for action in actions:
                if isinstance(action, dict):
                    result.add((event, matcher, str(action.get("type", ""))))
    return result


def check_hooks(root: Path, claude: dict[str, Any] | None, codex: dict[str, Any] | None, report: Report) -> None:
    paths: list[tuple[str, Path, dict[str, Any] | None]] = []
    for label, manifest, default in (
        ("Claude", claude, root / "hooks" / "hooks.json"),
        ("Codex", codex, root / "hooks.json"),
    ):
        if manifest is None:
            continue
        path = manifest_path(root, manifest, "hooks") or default
        if path.is_file():
            data = read_json(path, report)
            if data is not None and not isinstance(data.get("hooks"), dict):
                report.error(f"{label} hook config lacks outer 'hooks' object: {path}")
            paths.append((label, path, data))
    if len(paths) == 1:
        report.error(f"hooks are configured for {paths[0][0]} but not both harnesses")
    if len(paths) == 2 and paths[0][2] is not None and paths[1][2] is not None:
        if hook_signature(paths[0][2]) != hook_signature(paths[1][2]):
            report.error("Claude and Codex hook event/matcher/action signatures differ")


def server_names(data: dict[str, Any]) -> set[str]:
    servers = data.get("mcpServers")
    return set(servers) if isinstance(servers, dict) else set()


def check_mcp(root: Path, claude: dict[str, Any] | None, codex: dict[str, Any] | None, report: Report) -> None:
    configs: list[tuple[str, Path, dict[str, Any] | None]] = []
    for label, manifest, default in (
        ("Claude", claude, root / ".mcp.json"),
        ("Codex", codex, root / ".mcp.json"),
    ):
        if manifest is None:
            continue
        path = manifest_path(root, manifest, "mcpServers") or default
        if path.is_file():
            data = read_json(path, report)
            configs.append((label, path, data))
            if label == "Codex" and CLAUDE_TOKEN_RE.search(path.read_text(encoding="utf-8")):
                report.error(f"Codex MCP config contains a Claude-only token: {path}")
    if len(configs) == 1:
        report.error(f"MCP is configured for {configs[0][0]} but not both harnesses")
    if len(configs) == 2 and configs[0][2] is not None and configs[1][2] is not None:
        if server_names(configs[0][2]) != server_names(configs[1][2]):
            report.error("Claude and Codex MCP server names differ")


def check_host_only_surfaces(root: Path, report: Report) -> None:
    notes = root / "HARNESS-NOTES.md"
    for relative, harness in (
        ("output-styles", "Claude"),
        ("monitors", "Claude"),
        ("themes", "Claude"),
        (".lsp.json", "Claude"),
        (".app.json", "Codex"),
    ):
        path = root / relative
        if path.exists() and not notes.is_file():
            report.warn(
                f"{harness}-specific surface {relative} exists without HARNESS-NOTES.md fallback"
            )


def validate(root: Path) -> Report:
    report = Report()
    if not root.is_dir():
        report.error(f"plugin root is not a directory: {root}")
        return report
    claude = read_json(root / ".claude-plugin" / "plugin.json", report)
    codex = read_json(root / ".codex-plugin" / "plugin.json", report)
    check_manifest_pair(root, claude, codex, report)
    check_skills(root, claude, codex, report)
    check_agents_and_commands(root, claude, report)
    check_hooks(root, claude, codex, report)
    check_mcp(root, claude, codex, report)
    check_host_only_surfaces(root, report)
    return report


def print_report(root: Path, report: Report) -> None:
    verdict = "FAIL" if report.errors else "CLEAN"
    print(
        f"cross-harness validation · {root} · {verdict} · "
        f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)"
    )
    for message in report.errors:
        print(f"ERROR: {message}")
    for message in report.warnings:
        print(f"WARN: {message}")


def selftest() -> int:
    with tempfile.TemporaryDirectory(prefix="cross-harness-validator-") as tmp:
        root = Path(tmp) / "demo-plugin"
        (root / ".claude-plugin").mkdir(parents=True)
        (root / ".codex-plugin").mkdir(parents=True)
        skill = root / "skills" / "demo-skill"
        (skill / "agents").mkdir(parents=True)
        manifest = {
            "name": "demo-plugin",
            "version": "1.0.0",
            "description": "Demo plugin",
            "skills": "./skills/",
        }
        (root / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        (root / ".codex-plugin" / "plugin.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        (skill / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: Handles demo requests when asked.\n"
            "---\n\nDo the demo task.\n",
            encoding="utf-8",
        )
        (skill / "agents" / "openai.yaml").write_text(
            'interface:\n  display_name: "Demo Skill"\n', encoding="utf-8"
        )
        clean = validate(root)
        if clean.errors:
            print_report(root, clean)
            print("selftest: expected clean fixture to pass")
            return 1

        # Add representative skill, agent, command, hook, and MCP adapters.
        claude_skills = root / "adapters" / "claude" / "skills" / "demo-skill"
        claude_skills.mkdir(parents=True)
        (claude_skills / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: Handles demo requests when asked.\n"
            "disable-model-invocation: true\n---\n\nDo the demo task.\n",
            encoding="utf-8",
        )
        (skill / "agents" / "openai.yaml").write_text(
            'interface:\n  display_name: "Demo Skill"\npolicy:\n'
            "  allow_implicit_invocation: false\n",
            encoding="utf-8",
        )

        # Claude Code has no manifest field for relocating agents (verified, CLI 2.1.250) —
        # the co-located pattern (Claude frontmatter directly on the root file) is the only
        # working shape; Codex tolerates the leading frontmatter as non-body content.
        agent_body = "You are the demo reviewer.\n\nReturn findings and a verdict.\n"
        (root / "agents").mkdir()
        (root / "agents" / "reviewer.md").write_text(
            "---\nname: reviewer\ndescription: Reviews demo output when asked.\n---\n\n"
            + agent_body,
            encoding="utf-8",
        )

        (root / "commands").mkdir()
        (root / "commands" / "review.md").write_text(
            "# Review\n\nReview the target named in the current user request.\n",
            encoding="utf-8",
        )

        claude_hooks = root / "adapters" / "claude" / "hooks.json"
        claude_hooks.parent.mkdir(parents=True, exist_ok=True)
        hook_template = {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Write|Edit",
                        "hooks": [{"type": "command", "command": "COMMAND"}],
                    }
                ]
            }
        }
        codex_hook = json.loads(json.dumps(hook_template))
        codex_hook["hooks"]["PostToolUse"][0]["hooks"][0]["command"] = "./scripts/check.sh"
        claude_hook = json.loads(json.dumps(hook_template))
        claude_hook["hooks"]["PostToolUse"][0]["hooks"][0]["command"] = (
            '"${CLAUDE_PLUGIN_ROOT}"/scripts/check.sh'
        )
        (root / "hooks.json").write_text(json.dumps(codex_hook), encoding="utf-8")
        claude_hooks.write_text(json.dumps(claude_hook), encoding="utf-8")

        mcp = {
            "mcpServers": {
                "demo": {"type": "http", "url": "https://example.com/mcp"}
            }
        }
        (root / ".mcp.json").write_text(json.dumps(mcp), encoding="utf-8")

        claude_manifest = dict(manifest)
        claude_manifest.update(
            {
                "skills": "./adapters/claude/skills/",
                "commands": "./commands/",
                "hooks": "./adapters/claude/hooks.json",
                "mcpServers": "./.mcp.json",
            }
        )
        codex_manifest = dict(manifest)
        codex_manifest.update(
            {
                "mcpServers": "./.mcp.json",
            }
        )
        (root / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(claude_manifest), encoding="utf-8"
        )
        (root / ".codex-plugin" / "plugin.json").write_text(
            json.dumps(codex_manifest), encoding="utf-8"
        )
        complex_clean = validate(root)
        if complex_clean.errors:
            print_report(root, complex_clean)
            print("selftest: expected representative adapter fixture to pass")
            return 1

        # Negative controls: the invocation-policy parity checks — the script's most
        # behaviorally load-bearing branch (behavioral-fidelity.md rule 1). A human-only Claude
        # adapter whose Codex openai.yaml lacks allow_implicit_invocation: false must error;
        # the inverse (Codex explicit-only while Claude permits model invocation) must too.
        policy_yaml = (skill / "agents" / "openai.yaml")
        with_policy = policy_yaml.read_text(encoding="utf-8")
        policy_yaml.write_text('interface:\n  display_name: "Demo Skill"\n', encoding="utf-8")
        missing_policy = validate(root)
        if not any("does not set allow_implicit_invocation" in e for e in missing_policy.errors):
            print_report(root, missing_policy)
            print("selftest: expected human-only-without-Codex-policy to fail")
            return 1
        policy_yaml.write_text(with_policy, encoding="utf-8")
        adapter_sm = claude_skills / "SKILL.md"
        with_dmi = adapter_sm.read_text(encoding="utf-8")
        adapter_sm.write_text(with_dmi.replace(
            "disable-model-invocation: true", "disable-model-invocation: false"), encoding="utf-8")
        inverse_policy = validate(root)
        if not any("explicit-only while Claude permits" in e for e in inverse_policy.errors):
            print_report(root, inverse_policy)
            print("selftest: expected Codex-explicit-only-while-Claude-permits to fail")
            return 1
        adapter_sm.write_text(with_dmi, encoding="utf-8")

        # Negative control: an adapters/claude/agents/ tree can never be read by Claude
        # Code (no manifest field exists to relocate agents) — this must always error.
        claude_agents = root / "adapters" / "claude" / "agents"
        claude_agents.mkdir(parents=True)
        (claude_agents / "reviewer.md").write_text(
            "---\nname: reviewer\ndescription: Reviews demo output when asked.\n---\n\n"
            + agent_body,
            encoding="utf-8",
        )
        dead_adapter = validate(root)
        if not any(
            "no manifest field to relocate" in error for error in dead_adapter.errors
        ):
            print_report(root, dead_adapter)
            print("selftest: expected dead claude-agents adapter tree to fail")
            return 1
        shutil.rmtree(claude_agents)

        broken = dict(codex_manifest)
        broken["version"] = "2.0.0"
        (root / ".codex-plugin" / "plugin.json").write_text(
            json.dumps(broken), encoding="utf-8"
        )
        failed = validate(root)
        if not any("version" in error for error in failed.errors):
            print_report(root, failed)
            print("selftest: expected manifest drift to fail")
            return 1
    print("validate_cross_harness selftest · PASS")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "selftest":
        return selftest()
    if len(argv) != 2:
        print("usage: validate_cross_harness.py <plugin-root> | selftest", file=sys.stderr)
        return 2
    root = Path(argv[1]).expanduser().resolve()
    report = validate(root)
    print_report(root, report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
