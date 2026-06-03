#!/usr/bin/env node
/**
 * audit-axes.mjs — Universal audit axis library
 *
 * Composable audit functions for rollup-family skill audit scripts.
 * Per-skill `scripts/audit-<name>-roster.mjs` imports and composes these
 * with their own skill-specific axes.
 *
 * Usage:
 *   import * as axes from '${CLAUDE_PLUGIN_ROOT}/bin/lib/audit-axes.mjs';
 *   const result = axes.manifestEnforcement({ skillDir, skillMd, skillJson });
 *
 * Each function returns:
 *   { axis, axis_num, status: 'ok'|'drift', findings: [...], summary }
 *
 * All path arguments should be absolute.
 *
 * @module audit-axes
 */

import fs from 'node:fs';
import path from 'node:path';

// ─── helpers ──────────────────────────────────────────────────────────────────

/** Recursively walk a directory, returning relative paths of matching files. */
function walkDir(dir, { include = null, exclude = ['node_modules', '.git', 'docs'] } = {}) {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (exclude.some(x => entry.name === x)) continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...walkDir(fullPath, { include, exclude }));
    } else {
      if (!include || include.some(ext => entry.name.endsWith(ext))) {
        results.push(fullPath);
      }
    }
  }
  return results;
}

/** Read file; return '' if missing. */
function readSafe(p) {
  try { return fs.readFileSync(p, 'utf8'); } catch { return ''; }
}

/** Parse YAML frontmatter from a markdown file. Returns {} if none found. */
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};
  const result = {};
  for (const line of match[1].split('\n')) {
    const m = line.match(/^(\w+):\s*['"]?(.*?)['"]?\s*$/);
    if (m) result[m[1]] = m[2];
  }
  return result;
}

/** Extract all markdown links [text](path) from content, with line numbers. */
function extractMarkdownLinks(content, filePath) {
  const links = [];
  const lines = content.split('\n');
  let inFence = false;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^```/.test(line)) { inFence = !inFence; continue; }
    if (inFence) continue;
    // Strip inline code spans before checking for links (avoids false positives
    // like `[link](references/X.md)` used as format examples in documentation)
    const lineStripped = line.replace(/`[^`]*`/g, '``');
    // Match [text](url) but not [text](#anchor), http links, or mailto
    const re = /\[([^\]]*)\]\(([^)]+)\)/g;
    let m;
    while ((m = re.exec(lineStripped)) !== null) {
      const url = m[2];
      if (url.startsWith('http') || url.startsWith('#') || url.startsWith('mailto:')) continue;
      // Skip home-directory paths (shell paths, not relative file paths)
      if (url.startsWith('~/')) continue;
      // Skip template placeholders like <repo>, <name>, <path>
      if (/<[^>]+>/.test(url)) continue;
      // Skip bare single-word paths that look like example placeholders
      if (/^[a-z]+$/.test(url) && !url.includes('/')) continue;
      // Strip fragment
      const cleanUrl = url.split('#')[0];
      if (!cleanUrl) continue;
      links.push({ text: m[1], url: cleanUrl, line: i + 1, file: filePath });
    }
  }
  return links;
}

/** Make a finding object. */
function finding(type, message, extra = {}) {
  return { type, message, ...extra };
}

// ─── axes ──────────────────────────────────────────────────────────────────────

/**
 * Axis 1 (Manifest enforcement) — recursive walker.
 * Checks that skill.json files[] matches all content files on disk.
 * Reports both directions: on-disk-but-undeclared + declared-but-missing.
 *
 * Scans: references/, scripts/, evals/, assets/ (recursive) + top-level .md + .json (excl. skill.json itself)
 * Excludes: docs/ (refactor-specs), node_modules, .git
 *
 * @param {{ skillDir: string, skillJson: string }} ctx
 */
export function manifestEnforcement(ctx) {
  const { skillDir, skillJson } = ctx;
  const pkg = JSON.parse(readSafe(skillJson) || '{}');
  const declared = new Set((pkg.files || []).map(f => path.resolve(skillDir, f)));

  // Walk the skill directory for all content files
  const onDisk = new Set();

  // Top-level: *.md, *.json (except node_modules, docs/)
  for (const entry of fs.readdirSync(skillDir, { withFileTypes: true })) {
    if (!entry.isFile()) continue;
    if (!/\.(md|json|mjs|js)$/.test(entry.name)) continue;
    onDisk.add(path.join(skillDir, entry.name));
  }

  // Subdirectories: references/, scripts/, evals/, assets/ — recursive, excluding docs/
  for (const subDir of ['references', 'scripts', 'evals', 'assets']) {
    const full = path.join(skillDir, subDir);
    for (const f of walkDir(full, { include: ['.md', '.json', '.mjs', '.js', '.ts'] })) {
      onDisk.add(f);
    }
  }

  const undeclared = [...onDisk].filter(f => !declared.has(f))
    .map(f => path.relative(skillDir, f));
  const missing = [...declared].filter(f => !onDisk.has(f))
    .map(f => path.relative(skillDir, f));

  const status = (undeclared.length + missing.length) > 0 ? 'drift' : 'ok';
  const findings = [
    ...undeclared.map(f => finding('undeclared', `on disk but not in files[]: ${f}`, { path: f })),
    ...missing.map(f => finding('missing', `in files[] but not on disk: ${f}`, { path: f })),
  ];
  return {
    axis: 'manifestEnforcement',
    axis_num: 1,
    status,
    findings,
    summary: `${undeclared.length} undeclared, ${missing.length} missing`,
  };
}

/**
 * Axis 2 (Reference graph) — resolves markdown links in SKILL.md (and
 * optionally reference files). Reports links that don't resolve to an
 * existing file. Only checks relative links (ignores http://, #anchors,
 * mailto:, ~/ home paths, template placeholders).
 *
 * By default only scans SKILL.md. Pass `includeRefs: true` to also scan
 * reference files (reference files often contain example paths that produce
 * false positives — use with judgment).
 *
 * @param {{ skillDir: string, skillMd: string, includeRefs?: boolean }} ctx
 */
export function referenceGraph(ctx) {
  const { skillDir, skillMd, includeRefs = false } = ctx;
  const mdFiles = [skillMd];
  if (includeRefs) {
    mdFiles.push(...walkDir(path.join(skillDir, 'references'), { include: ['.md'] }));
  }

  const findings = [];
  for (const mdFile of mdFiles) {
    const content = readSafe(mdFile);
    const links = extractMarkdownLinks(content, mdFile);
    for (const { url, line, file } of links) {
      // Resolve relative to the containing .md file's directory
      const resolved = path.resolve(path.dirname(file), url);
      if (!fs.existsSync(resolved)) {
        const relFile = path.relative(skillDir, file);
        const relResolved = path.relative(skillDir, resolved);
        findings.push(finding('broken-link',
          `${relFile}:${line} → ${url} (resolves to ${relResolved}, not found)`,
          { file: relFile, line, url }
        ));
      }
    }
  }

  return {
    axis: 'referenceGraph',
    axis_num: 2,
    status: findings.length > 0 ? 'drift' : 'ok',
    findings,
    summary: `${findings.length} broken link(s)`,
  };
}

/**
 * Axis 3 (Capability-menu drift) — parses §ColdStartTriage table rows and
 * checks that each referenced entry-reference path exists on disk.
 * Handles both `[label](path)` link format and bare path format.
 *
 * @param {{ skillDir: string, skillMd: string }} ctx
 */
export function capabilityMenuDrift(ctx) {
  const { skillDir, skillMd } = ctx;
  const content = readSafe(skillMd);

  // Find §ColdStartTriage section
  const sectionMatch = content.match(
    /##\s+§ColdStartTriage[\s\S]*?(?=\n##\s+|$)/
  );
  if (!sectionMatch) {
    return {
      axis: 'capabilityMenuDrift',
      axis_num: 3,
      status: 'ok',
      findings: [],
      summary: 'No §ColdStartTriage section found (skip)',
    };
  }

  const section = sectionMatch[0];
  // Extract all markdown links within the section
  const links = extractMarkdownLinks(section, skillMd);
  // Also look for bare `references/X.md` patterns in the section (not in links)
  const barePaths = [...section.matchAll(/`(references\/[^`]+\.md)`/g)]
    .map(m => m[1]);

  const findings = [];

  for (const { url, text } of links) {
    if (!url.startsWith('references/') && !url.startsWith('../')) continue;
    const resolved = path.resolve(skillDir, url);
    if (!fs.existsSync(resolved)) {
      findings.push(finding('missing-entry-ref',
        `Mode entry ref missing: [${text}](${url})`,
        { url }
      ));
    }
  }

  for (const p of barePaths) {
    const resolved = path.join(skillDir, p);
    if (!fs.existsSync(resolved)) {
      findings.push(finding('missing-entry-ref',
        `Bare path in §ColdStartTriage not found: ${p}`,
        { url: p }
      ));
    }
  }

  return {
    axis: 'capabilityMenuDrift',
    axis_num: 3,
    status: findings.length > 0 ? 'drift' : 'ok',
    findings,
    summary: `${findings.length} missing entry-reference path(s)`,
  };
}

/**
 * Axis 4 (Version-literal parity) — checks that SKILL.md frontmatter version
 * matches skill.json version. Also scans the §Status section body for stale
 * version literals that don't match.
 *
 * @param {{ skillDir: string, skillMd: string, skillJson: string }} ctx
 */
export function versionLiteralParity(ctx) {
  const { skillMd, skillJson } = ctx;
  const content = readSafe(skillMd);
  const pkg = JSON.parse(readSafe(skillJson) || '{}');
  const jsonVersion = pkg.version || null;

  const findings = [];

  if (!jsonVersion) {
    findings.push(finding('no-version', 'skill.json has no version field'));
    return { axis: 'versionLiteralParity', axis_num: 4, status: 'drift', findings, summary: 'no version in skill.json' };
  }

  // Check frontmatter version
  const fm = parseFrontmatter(content);
  if (fm.version && fm.version !== jsonVersion) {
    findings.push(finding('frontmatter-drift',
      `SKILL.md frontmatter version: ${fm.version} ≠ skill.json: ${jsonVersion}`
    ));
  }

  // Scan §Status section body for "Version X.Y.Z" or "vX.Y.Z" stale mentions
  const statusMatch = content.match(/##\s+§Status([\s\S]*?)(?=\n##\s+|$)/);
  if (statusMatch) {
    const statusBody = statusMatch[1];
    // Find any version that looks like a semver but isn't the current one
    const versionRe = /\bv?(\d+\.\d+\.\d+)\b/g;
    let m;
    while ((m = versionRe.exec(statusBody)) !== null) {
      const found = m[1];
      if (found !== jsonVersion) {
        findings.push(finding('status-section-stale',
          `§Status body contains version ${found} ≠ skill.json ${jsonVersion} — §Status should only point at CHANGELOG.md`
        ));
      }
    }
  }

  return {
    axis: 'versionLiteralParity',
    axis_num: 4,
    status: findings.length > 0 ? 'drift' : 'ok',
    findings,
    summary: findings.length > 0 ? `${findings.length} version-literal mismatch(es)` : `all literals match ${jsonVersion}`,
  };
}

/**
 * Axis 5 (Phase-label absence) — searches SKILL.md body for stale phase
 * annotations: "(Phase 1)", "(Phase 2 — planned)", "Phase 4 (v1.0.0, this)",
 * etc. These should have been removed as part of Round 0 cleanup.
 *
 * @param {{ skillMd: string }} ctx
 */
export function phaseLabelAbsence(ctx) {
  const { skillMd } = ctx;
  const content = readSafe(skillMd);
  const lines = content.split('\n');

  const findings = [];
  const phaseRe = /\(Phase\s+\d+[\w\s—.]*\)|Phase\s+\d+\s*\(v\d+\.\d+\.\d+|Phase\s+\d+\s+references\s*\(planned\)/i;

  for (let i = 0; i < lines.length; i++) {
    if (phaseRe.test(lines[i])) {
      findings.push(finding('phase-label',
        `Line ${i + 1}: stale phase annotation — ${lines[i].trim()}`,
        { line: i + 1, content: lines[i].trim() }
      ));
    }
  }

  return {
    axis: 'phaseLabelAbsence',
    axis_num: 5,
    status: findings.length > 0 ? 'drift' : 'ok',
    findings,
    summary: `${findings.length} stale phase label(s)`,
  };
}

/**
 * Axis 6 (Fence-leak detection) — scans SKILL.md for H2/H3 headings inside
 * fenced code blocks that are NOT ``` markdown / md / mdx ``` type.
 * These are typically fence-close mistakes where a heading leaked into
 * a code block.
 *
 * @param {{ skillMd: string }} ctx
 */
export function fenceLeakDetection(ctx) {
  const { skillMd } = ctx;
  const content = readSafe(skillMd);
  const lines = content.split('\n');

  const findings = [];
  let inFence = false;
  let fenceLang = '';
  let fenceStart = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const fenceOpen = line.match(/^```(\w*)/);

    if (fenceOpen && !inFence) {
      inFence = true;
      fenceLang = fenceOpen[1].toLowerCase();
      fenceStart = i + 1;
      continue;
    }

    if (inFence && line.startsWith('```') && !line.startsWith('````')) {
      inFence = false;
      fenceLang = '';
      continue;
    }

    if (inFence) {
      // Headings inside markdown fences are intentional (templates)
      if (['markdown', 'md', 'mdx'].includes(fenceLang)) continue;
      // Headings inside non-markdown fences are likely fence-leak bugs
      if (/^#{2,3}\s/.test(line)) {
        findings.push(finding('fence-leak',
          `Line ${i + 1}: heading inside \`\`\`${fenceLang}\`\`\` fence — ${line.trim()}`,
          { line: i + 1, fenceLang, content: line.trim() }
        ));
      }
    }
  }

  return {
    axis: 'fenceLeakDetection',
    axis_num: 6,
    status: findings.length > 0 ? 'drift' : 'ok',
    findings,
    summary: `${findings.length} fence-leak heading(s)`,
  };
}

/**
 * Axis 7 (Content currency) — verifies that paths in skill.json files[]
 * actually exist. A missing file means the manifest is stale (probably a
 * file was moved or deleted without updating the manifest).
 * Note: this overlaps with manifestEnforcement's "declared-but-missing"
 * direction; use that for bidirectional checks, this for declaration-only.
 *
 * @param {{ skillDir: string, skillJson: string }} ctx
 */
export function contentCurrency(ctx) {
  const { skillDir, skillJson } = ctx;
  const pkg = JSON.parse(readSafe(skillJson) || '{}');
  const declared = pkg.files || [];

  const findings = [];
  for (const relPath of declared) {
    const full = path.resolve(skillDir, relPath);
    if (!fs.existsSync(full)) {
      findings.push(finding('missing-declared',
        `Declared in files[] but not on disk: ${relPath}`,
        { path: relPath }
      ));
    }
  }

  return {
    axis: 'contentCurrency',
    axis_num: 7,
    status: findings.length > 0 ? 'drift' : 'ok',
    findings,
    summary: `${findings.length} declared-but-missing file(s)`,
  };
}

/**
 * Axis 8 (CLI helper currency) — scans SKILL.md for `npm run X` and
 * `node scripts/Y` patterns and checks they resolve. Scripts labeled
 * `(substrate-only)` or `(monorepo only)` are skipped.
 * Requires repoRoot to resolve package.json for npm run checks.
 *
 * @param {{ skillDir: string, skillMd: string, repoRoot?: string }} ctx
 */
export function cliHelperCurrency(ctx) {
  const { skillDir, skillMd, repoRoot } = ctx;
  const content = readSafe(skillMd);

  const findings = [];

  // Parse package.json scripts if repoRoot provided
  let pkgScripts = null;
  if (repoRoot) {
    try {
      const pkgJson = JSON.parse(fs.readFileSync(path.join(repoRoot, 'package.json'), 'utf8'));
      pkgScripts = pkgJson.scripts || {};
    } catch { /* repoRoot doesn't have package.json */ }
  }

  // Skip lines with (substrate-only) or (monorepo only) annotations
  const lines = content.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/(substrate.only|monorepo.only)/i.test(line)) continue;
    // Skip comment lines
    if (/^\s*(#|\/\/)/.test(line)) continue;

    // npm run X
    const npmRe = /`npm run ([\w:.-]+)`/g;
    let m;
    while ((m = npmRe.exec(line)) !== null) {
      const scriptName = m[1];
      if (pkgScripts && !pkgScripts[scriptName]) {
        findings.push(finding('missing-npm-script',
          `Line ${i + 1}: npm run ${scriptName} not found in package.json scripts`,
          { line: i + 1, script: scriptName }
        ));
      }
    }

    // node scripts/X.mjs or node skills/.../scripts/X.mjs
    const nodeRe = /`node\s+(skills\/[^\s`]+|scripts\/[^\s`]+)`/g;
    while ((m = nodeRe.exec(line)) !== null) {
      const scriptPath = m[1];
      // Resolve relative to repoRoot if available, otherwise skillDir
      const base = repoRoot || skillDir;
      const resolved = path.resolve(base, scriptPath);
      if (!fs.existsSync(resolved)) {
        findings.push(finding('missing-script',
          `Line ${i + 1}: node ${scriptPath} — file not found`,
          { line: i + 1, scriptPath }
        ));
      }
    }
  }

  return {
    axis: 'cliHelperCurrency',
    axis_num: 8,
    status: findings.length > 0 ? 'drift' : 'ok',
    findings,
    summary: `${findings.length} missing CLI helper(s)`,
  };
}

// ─── convenience: run a standard set ──────────────────────────────────────────

/**
 * Run all 8 universal axes and return results.
 * Per-skill scripts call this then append their own axes.
 *
 * @param {{ skillDir: string, skillMd: string, skillJson: string, repoRoot?: string }} ctx
 * @returns {{ results: object[], driftCount: number }}
 */
export function runUniversalAxes(ctx) {
  const axeFns = [
    manifestEnforcement,
    referenceGraph,
    capabilityMenuDrift,
    versionLiteralParity,
    phaseLabelAbsence,
    fenceLeakDetection,
    contentCurrency,
    cliHelperCurrency,
  ];

  const results = axeFns.map(fn => fn(ctx));
  const driftCount = results.filter(r => r.status === 'drift').length;
  return { results, driftCount };
}

/**
 * Format a results array as human-readable text.
 * @param {object[]} results
 * @param {{ strict?: boolean, json?: boolean }} opts
 */
export function formatResults(results, opts = {}) {
  if (opts.json) return JSON.stringify({ results }, null, 2);

  const lines = [];
  for (const r of results) {
    const icon = r.status === 'ok' ? '✓' : '✗';
    lines.push(`${icon} ${r.axis}: ${r.summary}`);
    if (r.status === 'drift' && r.findings.length > 0) {
      for (const f of r.findings) {
        lines.push(`    ${f.type}: ${f.message}`);
      }
    }
  }
  return lines.join('\n');
}
