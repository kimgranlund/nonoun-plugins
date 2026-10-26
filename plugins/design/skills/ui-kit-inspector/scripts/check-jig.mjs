#!/usr/bin/env node
// Check that a page meets the jig contract, in Chromium.
//
//   node check-jig.mjs <page.html or http URL> [--save <file>]
//     prints one line per check: "pass <id> <detail>", "fail <id> <detail>" or "skip <id> <detail>"
//     exit 0  nothing failed
//     exit 1  a check failed
//     exit 2  prints "cannot check: <reason>" (no Playwright, no browser, the page does not load)
//
// Playwright is not shipped with the skill. It is loaded from the folder you run this in,
// then from the page's folder, so run it from a project that has Playwright installed.
//
// The checks:
//   load         no console error and no uncaught page error, from navigation to the end of the run
//   markers      one [data-jig] with a known kind, one [data-jig-canvas], at least one [data-jig-constant]
//   changeset    window.jig.changeSet() validates, its kind equals data-jig, and changes is empty at load
//   edit         ArrowUp in the first visible number constant gives exactly one change, with that control's path
//   refuse-base  importSet refuses that change set once its base identity is altered, and applies nothing
//   refuse-from  importSet refuses it once the first change's from is altered, and applies nothing
//   round-trip   importSet takes the unaltered change set and changes equals what was exported
// With --save, the change set captured by the edit check is written to the file.

import { existsSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { validate } from "./validate-changeset.mjs";

const KINDS = ["system", "component", "layout", "theme"];
const NUMBER_CONTROL = "input[type=number], [role=spinbutton]";

class CannotCheck extends Error {}

function parseArgs(args) {
  let target = null;
  let save = null;
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === "--save" && args[i + 1]) save = args[(i += 1)];
    else if (target === null && !args[i].startsWith("--")) target = args[i];
    else throw new CannotCheck("usage: node check-jig.mjs <page.html or http URL> [--save <file>]");
  }
  if (target === null) throw new CannotCheck("usage: node check-jig.mjs <page.html or http URL> [--save <file>]");
  return { target, save };
}

function locate(target) {
  if (/^https?:\/\//.test(target)) return { url: target, folder: null };
  const file = path.resolve(target);
  if (!existsSync(file)) throw new CannotCheck(`no such page: ${file}`);
  return { url: pathToFileURL(file).href, folder: path.dirname(file) };
}

function loadPlaywright(folders) {
  for (const folder of folders) {
    try {
      return createRequire(folder + path.sep)("playwright");
    } catch (error) {
      if (error.code !== "MODULE_NOT_FOUND") throw new CannotCheck(`playwright failed to load from ${folder}: ${error.message}`);
    }
  }
  throw new CannotCheck(`playwright does not resolve from ${folders.join(" or ")}; run this from a project that has it installed`);
}

function equal(a, b) {
  if (a === b) return true;
  if (a === null || b === null || typeof a !== "object" || typeof b !== "object" || Array.isArray(a) !== Array.isArray(b)) return false;
  const keys = Object.keys(a);
  return keys.length === Object.keys(b).length && keys.every((key) => Object.hasOwn(b, key) && equal(a[key], b[key]));
}

// A copy of the change set that claims another base. Null when it names no identity to alter.
function withAlteredBase(set) {
  const copy = structuredClone(set);
  let altered = false;
  for (const key of ["sha256", "version", "revision"]) {
    const value = copy.base?.[key];
    if (typeof value !== "string" || value === "") continue;
    copy.base[key] = key === "sha256" ? (value[0] === "0" ? "1" : "0") + value.slice(1) : `${value}-altered`;
    altered = true;
  }
  return altered ? copy : null;
}

// A copy whose first change claims another starting value, one that still differs from its to.
function withAlteredFrom(set) {
  const copy = structuredClone(set);
  const change = copy.changes[0];
  if (typeof change.from === "number") change.from = [change.from - 1, change.from + 1].find((value) => value !== change.to);
  else change.from = `${change.from}-altered`;
  return copy;
}

const readSet = (page) =>
  page.evaluate(() => {
    if (!window.jig || typeof window.jig.changeSet !== "function") return { error: "window.jig.changeSet is not a function" };
    try {
      return { set: window.jig.changeSet() };
    } catch (error) {
      return { error: `window.jig.changeSet() threw: ${error && error.message}` };
    }
  });

const importAndRead = (page, set) =>
  page.evaluate((text) => {
    if (typeof window.jig.importSet !== "function") return { error: "window.jig.importSet is not a function" };
    try {
      const refusals = window.jig.importSet(text);
      return { refusals, changes: window.jig.changeSet().changes };
    } catch (error) {
      return { error: `window.jig.importSet() threw: ${error && error.message}` };
    }
  }, JSON.stringify(set));

async function runChecks(page, url, save) {
  const results = [];
  const record = (status, id, detail) => results.push({ status, id, detail });
  const problems = [];
  page.on("console", (message) => {
    if (message.type() === "error") problems.push(`console error: ${message.text()}`);
  });
  page.on("pageerror", (error) => problems.push(`page error: ${error.message}`));

  try {
    await page.goto(url, { waitUntil: "load" });
  } catch (error) {
    throw new CannotCheck(`the page did not load: ${error.message.split("\n")[0]}`);
  }

  // markers
  const marks = await page.evaluate(() => ({
    kinds: Array.from(document.querySelectorAll("[data-jig]"), (el) => el.getAttribute("data-jig")),
    canvases: document.querySelectorAll("[data-jig-canvas]").length,
    constants: document.querySelectorAll("[data-jig-constant]").length,
  }));
  const markerFaults = [];
  if (marks.kinds.length !== 1) markerFaults.push(`${marks.kinds.length} [data-jig] elements, expected 1`);
  else if (!KINDS.includes(marks.kinds[0])) markerFaults.push(`data-jig is "${marks.kinds[0]}", expected one of ${KINDS.join(", ")}`);
  if (marks.canvases !== 1) markerFaults.push(`${marks.canvases} [data-jig-canvas] elements, expected 1`);
  if (marks.constants < 1) markerFaults.push("no [data-jig-constant]");
  if (markerFaults.length) record("fail", "markers", markerFaults.join("; "));
  else record("pass", "markers", `data-jig="${marks.kinds[0]}", 1 canvas, ${marks.constants} constant${marks.constants === 1 ? "" : "s"}`);

  // changeset
  const atLoad = await readSet(page);
  if (atLoad.error) {
    record("fail", "changeset", atLoad.error);
  } else {
    const faults = validate(atLoad.set);
    if (!faults.length && atLoad.set.kind !== marks.kinds[0]) faults.push(`kind is "${atLoad.set.kind}" but data-jig is "${marks.kinds[0]}"`);
    if (!faults.length && atLoad.set.changes.length !== 0) faults.push(`${atLoad.set.changes.length} changes at load, expected none`);
    if (faults.length) record("fail", "changeset", faults.join("; "));
    else record("pass", "changeset", `valid ${atLoad.set.$schema}, kind ${atLoad.set.kind}, no changes at load`);
  }

  // edit
  let exported = null;
  if (atLoad.error) {
    record("skip", "edit", "no change set to read");
  } else {
    const picked = await page.evaluate((selector) => {
      for (const holder of document.querySelectorAll("[data-jig-constant]")) {
        const control = holder.matches(selector) ? holder : holder.querySelector(selector);
        if (!control || !control.checkVisibility({ visibilityProperty: true })) continue;
        control.focus();
        return { path: holder.getAttribute("data-jig-constant") };
      }
      return null;
    }, NUMBER_CONTROL);
    if (!picked) {
      record("skip", "edit", `no visible [data-jig-constant] is or contains ${NUMBER_CONTROL}`);
    } else {
      await page.keyboard.press("ArrowUp");
      const after = await readSet(page);
      const faults = [];
      if (after.error) faults.push(after.error);
      else {
        faults.push(...validate(after.set));
        const changes = Array.isArray(after.set?.changes) ? after.set.changes : [];
        if (changes.length !== 1) faults.push(`${changes.length} changes after ArrowUp in ${picked.path}, expected 1`);
        else if (changes[0].path !== picked.path) faults.push(`the change is at ${changes[0].path}, but the control says ${picked.path}`);
      }
      if (faults.length) {
        record("fail", "edit", faults.join("; "));
      } else {
        exported = after.set;
        const change = exported.changes[0];
        let saved = "";
        if (save) {
          try {
            writeFileSync(save, `${JSON.stringify(exported, null, 2)}\n`);
          } catch (error) {
            throw new CannotCheck(`cannot write ${save}: ${error.message}`);
          }
          saved = `, saved to ${save}`;
        }
        record("pass", "edit", `ArrowUp moved ${change.path} from ${change.from} to ${change.to}${saved}`);
      }
    }
  }

  // refuse-base, refuse-from, round-trip
  if (!exported) {
    for (const id of ["refuse-base", "refuse-from", "round-trip"]) record("skip", id, "the edit check gave no change set to import");
  } else {
    const refusal = async (id, altered, what) => {
      if (!altered) return record("skip", id, `the change set has no ${what} to alter`);
      const out = await importAndRead(page, altered);
      if (out.error) return record("fail", id, out.error);
      if (!Array.isArray(out.refusals) || out.refusals.length === 0) return record("fail", id, `importSet accepted a change set with an altered ${what}`);
      if (!equal(out.changes, exported.changes)) return record("fail", id, "importSet refused, but the changes moved");
      return record("pass", id, `refused: ${out.refusals[0]}`);
    };
    await refusal("refuse-base", withAlteredBase(exported), "base identity");
    await refusal("refuse-from", withAlteredFrom(exported), "from");

    const back = await importAndRead(page, exported);
    if (back.error) record("fail", "round-trip", back.error);
    else if (!Array.isArray(back.refusals)) record("fail", "round-trip", "importSet did not return an array");
    else if (back.refusals.length) record("fail", "round-trip", `importSet refused its own export: ${back.refusals[0]}`);
    else if (!equal(back.changes, exported.changes)) record("fail", "round-trip", "the changes after import differ from the export");
    else record("pass", "round-trip", `${exported.changes.length} change imported and exported again unchanged`);
  }

  // load is judged last: it covers the whole run.
  if (problems.length) results.unshift({ status: "fail", id: "load", detail: problems.join("; ") });
  else results.unshift({ status: "pass", id: "load", detail: "no console error, no page error" });
  return results;
}

async function main(args) {
  const { target, save } = parseArgs(args);
  const { url, folder } = locate(target);
  const { chromium } = loadPlaywright([process.cwd(), folder].filter(Boolean));
  let browser;
  try {
    browser = await chromium.launch();
  } catch (error) {
    throw new CannotCheck(`Chromium did not start: ${error.message.split("\n")[0]}`);
  }
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
    const results = await runChecks(page, url, save);
    for (const result of results) console.log(`${result.status} ${result.id} ${result.detail}`);
    return results.some((result) => result.status === "fail") ? 1 : 0;
  } finally {
    await browser.close();
  }
}

main(process.argv.slice(2)).then(
  (code) => {
    process.exitCode = code;
  },
  (error) => {
    console.log(`cannot check: ${error instanceof CannotCheck ? error.message : (error.stack ?? error)}`);
    process.exitCode = 2;
  },
);
