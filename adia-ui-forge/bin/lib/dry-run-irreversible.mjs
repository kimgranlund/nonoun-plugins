#!/usr/bin/env node
/**
 * dry-run-irreversible.mjs — Dry-run preview + confirmation for irreversible ops
 *
 * Wraps operations like `git push`, `npm publish`, `systemctl restart`,
 * `gh release create` with a preview step and blast-radius-appropriate
 * confirmation gate.
 *
 * Usage (per-skill script):
 *   import { executeWithAuthorization, isDryRunMode } from
 *     '${CLAUDE_PLUGIN_ROOT}/bin/lib/dry-run-irreversible.mjs';
 *
 *   const result = await executeWithAuthorization({
 *     action: 'Publish @acme/kit@1.4.0 to npm',
 *     blastRadius: 'high',
 *     dryRun: async () => `npm pack --dry-run output:\n  kit-1.4.0.tgz (42 kB)`,
 *     apply: async () => { execSync('npm publish --access public', { stdio: 'inherit' }); },
 *     options: { dryRunOnly: isDryRunMode() },
 *   });
 *
 * @module dry-run-irreversible
 */

import readline from 'node:readline';

// ─── constants ────────────────────────────────────────────────────────────────

const BLAST_CONFIG = {
  low: {
    symbol: '✓',
    label: 'LOW BLAST RADIUS',
    note: 'local/reversible',
    color: '\x1b[32m',       // green
    requireYes: false,
    autoApprove: true,
  },
  medium: {
    symbol: '⚡',
    label: 'MEDIUM BLAST RADIUS',
    note: 'shared state, reversible with effort',
    color: '\x1b[33m',       // yellow
    requireYes: false,
    autoApprove: false,
  },
  high: {
    symbol: '⚠',
    label: 'HIGH BLAST RADIUS',
    note: 'irreversible (publish/push/ssh-write)',
    color: '\x1b[31m',       // red
    requireYes: true,
    autoApprove: false,
  },
};

const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';

// ─── helpers ──────────────────────────────────────────────────────────────────

/**
 * Return a formatted blast-radius label string for display.
 * @param {'low'|'medium'|'high'} br
 * @returns {string}
 */
export function blastRadiusLabel(br) {
  const cfg = BLAST_CONFIG[br];
  if (!cfg) throw new Error(`Unknown blastRadius: ${br}`);
  return `${cfg.color}${BOLD}${cfg.symbol} ${cfg.label}${RESET} — ${cfg.note}`;
}

/**
 * Check whether the current process was invoked with --dry-run or DRY_RUN=1.
 * @returns {boolean}
 */
export function isDryRunMode() {
  return process.argv.includes('--dry-run') || process.env.DRY_RUN === '1';
}

/**
 * Default stdin prompter. Reads one line from stdin.
 * @param {string} question
 * @returns {Promise<string>}
 */
function stdinPrompter(question) {
  return new Promise(resolve => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      terminal: true,
    });
    rl.question(question, answer => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

// ─── core export ──────────────────────────────────────────────────────────────

/**
 * Execute an irreversible operation with dry-run preview and confirmation.
 *
 * @param {{
 *   action: string,
 *   dryRun: () => Promise<string>,
 *   apply: () => Promise<any>,
 *   blastRadius: 'low'|'medium'|'high',
 *   options?: {
 *     autoApprove?: boolean,
 *     force?: boolean,
 *     dryRunOnly?: boolean,
 *     prompter?: (q: string) => Promise<string>
 *   }
 * }} params
 *
 * @returns {Promise<{
 *   status: 'applied'|'declined'|'dry-run-only'|'applied-forced',
 *   result?: any,
 *   preview?: string,
 *   reason?: string
 * }>}
 */
export async function executeWithAuthorization({ action, dryRun, apply, blastRadius, options = {} }) {
  if (!action) throw new Error('action is required');
  if (typeof dryRun !== 'function') throw new Error('dryRun must be an async function');
  if (typeof apply !== 'function') throw new Error('apply must be an async function');

  const cfg = BLAST_CONFIG[blastRadius];
  if (!cfg) throw new Error(`blastRadius must be 'low', 'medium', or 'high'`);

  const {
    autoApprove: autoApproveOpt,
    force = false,
    dryRunOnly = false,
    prompter = stdinPrompter,
  } = options;

  // force skips everything — dangerous but explicit
  if (force) {
    const result = await apply();
    return { status: 'applied-forced', result, reason: '--force flag bypassed confirmation' };
  }

  // Always run the dry-run preview first
  let preview;
  try {
    preview = await dryRun();
  } catch (err) {
    throw new Error(`dryRun() threw: ${err.message}`);
  }

  // Print blast-radius warning (prominent for high)
  if (blastRadius === 'high') {
    console.log(`\n${cfg.color}${BOLD}${'─'.repeat(60)}${RESET}`);
    console.log(blastRadiusLabel(blastRadius));
    console.log(`${cfg.color}${BOLD}${'─'.repeat(60)}${RESET}\n`);
  } else {
    console.log(`\n${blastRadiusLabel(blastRadius)}\n`);
  }

  console.log(`${BOLD}Action:${RESET} ${action}`);
  console.log(`\n${BOLD}Dry-run preview:${RESET}`);
  console.log(preview);

  if (dryRunOnly) {
    console.log('\n(dry-run-only mode — not applying)');
    return { status: 'dry-run-only', preview };
  }

  // Auto-approve low blast radius unless explicitly disabled
  const canAutoApprove = (autoApproveOpt ?? cfg.autoApprove) && blastRadius === 'low';
  if (canAutoApprove) {
    console.log(`\n${BLAST_CONFIG.low.color}Auto-approved (low blast radius).${RESET}`);
    const result = await apply();
    return { status: 'applied', result, preview };
  }

  // Prompt for confirmation
  let answer;
  if (cfg.requireYes) {
    answer = await prompter(`\nType ${BOLD}yes${RESET} to confirm, anything else to abort: `);
    if (answer !== 'yes') {
      console.log('Aborted.');
      return { status: 'declined', preview, reason: `User typed '${answer}' instead of 'yes'` };
    }
  } else {
    answer = await prompter('\nApply? [y/N] ');
    if (!/^y(es)?$/i.test(answer)) {
      console.log('Aborted.');
      return { status: 'declined', preview, reason: 'User declined' };
    }
  }

  const result = await apply();
  console.log('\nApplied.');
  return { status: 'applied', result, preview };
}

// ─── convenience wrapper ──────────────────────────────────────────────────────

/**
 * Wrap a CLI script's main function with dry-run / blast-radius handling.
 * The returned function accepts raw CLI args and calls back into the script.
 *
 * @param {(args: string[]) => Promise<any>} script
 * @param {{ action: string, blastRadius: 'low'|'medium'|'high' }} meta
 * @returns {(args: string[]) => Promise<{
 *   status: 'applied'|'declined'|'dry-run-only'|'applied-forced',
 *   result?: any,
 *   preview?: string
 * }>}
 */
export function wrapScript(script, { action, blastRadius }) {
  return async function wrappedScript(args = []) {
    const isDry = args.includes('--dry-run') || isDryRunMode();
    const isForce = args.includes('--force');

    return executeWithAuthorization({
      action,
      blastRadius,
      dryRun: async () => {
        // Scripts that support --dry-run should honour the flag themselves
        const dryArgs = isDry ? args : [...args, '--dry-run'];
        return `(preview from script with args: ${dryArgs.join(' ')})`;
      },
      apply: async () => script(args),
      options: {
        dryRunOnly: isDry && !isForce,
        force: isForce,
      },
    });
  };
}
