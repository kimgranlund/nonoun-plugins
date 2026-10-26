#!/usr/bin/env node
// Validate a jig change set (jig.changeset/1). No dependency.
//
//   node validate-changeset.mjs <file.json>
//     exit 0  prints "valid"
//     exit 1  prints one line per error: "invalid <json pointer>: <message>"
//     exit 2  prints "cannot validate: <reason>" (the file is unreadable or not JSON,
//             or the schema uses a keyword this file does not interpret)
//
//   import { validate } from "./validate-changeset.mjs"
//     validate(changeSet) returns the same lines as an array, empty when valid.
//
// The shape comes from ../schema/changeset.schema.json, which this file interprets.
// Three rules a schema cannot say are written here: R1, R2 and R3 (see rules()).
// The pointer names the object that holds the problem. The root is written "/".

import { readFileSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

const SCHEMA_URL = new URL("../schema/changeset.schema.json", import.meta.url);
const KEYWORDS = new Set(["type", "properties", "required", "additionalProperties", "items", "enum", "const", "pattern", "minLength", "anyOf", "$ref"]);
const ANNOTATIONS = new Set(["$schema", "title", "description", "definitions"]);
const REF_PREFIX = "#/definitions/";

const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const typeOf = (v) => (v === null ? "null" : Array.isArray(v) ? "array" : typeof v);
const escape = (key) => String(key).replace(/~/g, "~0").replace(/\//g, "~1");
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

let cached;
function loadSchema() {
  if (cached) return cached;
  let schema;
  try {
    schema = JSON.parse(readFileSync(SCHEMA_URL, "utf8"));
  } catch (error) {
    throw new Error(`cannot read the schema ${fileURLToPath(SCHEMA_URL)}: ${error.message}`);
  }
  vet(schema, schema, "");
  cached = schema;
  return schema;
}

// Refuse a schema this file cannot interpret, so a keyword is never silently skipped.
function vet(schema, root, at) {
  if (!isObject(schema)) throw new Error(`schema at ${at || "/"} is not an object`);
  for (const key of Object.keys(schema)) {
    if (!KEYWORDS.has(key) && !ANNOTATIONS.has(key)) throw new Error(`schema keyword ${key} at ${at || "/"} is not supported`);
  }
  if (schema.$ref !== undefined) deref(schema.$ref, root);
  for (const group of ["properties", "definitions"]) {
    if (schema[group] === undefined) continue;
    if (!isObject(schema[group])) throw new Error(`schema ${group} at ${at || "/"} is not an object`);
    for (const [key, sub] of Object.entries(schema[group])) vet(sub, root, `${at}/${group}/${escape(key)}`);
  }
  if (schema.items !== undefined) vet(schema.items, root, `${at}/items`);
  if (schema.additionalProperties !== undefined && typeof schema.additionalProperties !== "boolean") vet(schema.additionalProperties, root, `${at}/additionalProperties`);
  if (schema.anyOf !== undefined) {
    if (!Array.isArray(schema.anyOf)) throw new Error(`schema anyOf at ${at || "/"} is not an array`);
    schema.anyOf.forEach((sub, i) => vet(sub, root, `${at}/anyOf/${i}`));
  }
}

function deref(ref, root) {
  const name = typeof ref === "string" && ref.startsWith(REF_PREFIX) ? ref.slice(REF_PREFIX.length) : null;
  const target = name && isObject(root.definitions) ? root.definitions[name] : undefined;
  if (target === undefined) throw new Error(`schema $ref ${JSON.stringify(ref)} does not resolve; only ${REF_PREFIX}<name> is supported`);
  return target;
}

// Walk one schema node against one value. Errors are { at, message }.
function check(schema, value, at, root, errors) {
  if (schema.$ref !== undefined) check(deref(schema.$ref, root), value, at, root, errors);

  const actual = typeOf(value);
  if (schema.type !== undefined) {
    const types = [].concat(schema.type);
    const ok = types.some((t) => t === actual || (t === "integer" && actual === "number" && Number.isInteger(value)));
    if (!ok) {
      errors.push({ at, message: `expected ${types.join(" or ")}, got ${actual}` });
      return;
    }
  }
  if (schema.const !== undefined && !same(schema.const, value)) errors.push({ at, message: `must be ${JSON.stringify(schema.const)}` });
  if (schema.enum !== undefined && !schema.enum.some((option) => same(option, value))) errors.push({ at, message: `must be one of ${schema.enum.join(", ")}` });

  if (actual === "string") {
    if (schema.minLength !== undefined && [...value].length < schema.minLength) errors.push({ at, message: schema.minLength === 1 ? "must not be empty" : `is shorter than ${schema.minLength} characters` });
    if (schema.pattern !== undefined && !new RegExp(schema.pattern).test(value)) errors.push({ at, message: `does not match ${schema.pattern}` });
  }

  if (actual === "object") {
    for (const key of schema.required ?? []) {
      if (!Object.hasOwn(value, key)) errors.push({ at, message: `missing required key ${key}` });
    }
    const known = schema.properties ?? {};
    for (const key of Object.keys(value)) {
      const here = `${at}/${escape(key)}`;
      if (Object.hasOwn(known, key)) check(known[key], value[key], here, root, errors);
      else if (schema.additionalProperties === false) errors.push({ at, message: `unknown key ${key}` });
      else if (isObject(schema.additionalProperties)) check(schema.additionalProperties, value[key], here, root, errors);
    }
  }

  if (actual === "array" && schema.items !== undefined) {
    value.forEach((item, i) => check(schema.items, item, `${at}/${i}`, root, errors));
  }

  if (schema.anyOf !== undefined) {
    const branches = schema.anyOf.map((sub) => {
      const found = [];
      check(sub, value, at, root, found);
      return found;
    });
    if (!branches.some((found) => found.length === 0)) {
      const why = branches.map((found) => (found[0].at === at ? found[0].message : `${found[0].at}: ${found[0].message}`));
      errors.push({ at, message: `none of the alternatives holds (${why.join(" | ")})` });
    }
  }
}

// The rules a schema cannot say.
//   R1  from differs from to in every change and override.
//   R2  change paths are unique.
//   R3  in each non-null check, passed is true exactly when failures is empty.
function rules(set, errors) {
  if (!isObject(set)) return;
  const seen = new Map();
  for (const group of ["changes", "overrides"]) {
    if (!Array.isArray(set[group])) continue;
    set[group].forEach((entry, i) => {
      if (!isObject(entry)) return;
      const at = `/${group}/${i}`;
      if (Object.hasOwn(entry, "from") && Object.hasOwn(entry, "to") && entry.from === entry.to) {
        errors.push({ at, message: `R1 from equals to (${JSON.stringify(entry.to)}), so nothing changes` });
      }
      if (group !== "changes" || typeof entry.path !== "string") return;
      if (seen.has(entry.path)) errors.push({ at, message: `R2 path ${entry.path} is already changed at /changes/${seen.get(entry.path)}` });
      else seen.set(entry.path, i);
    });
  }
  if (!isObject(set.checks)) return;
  for (const name of ["contract", "proposed"]) {
    const group = set.checks[name];
    if (!isObject(group) || typeof group.passed !== "boolean" || !Array.isArray(group.failures)) continue;
    const at = `/checks/${name}`;
    if (group.passed && group.failures.length > 0) errors.push({ at, message: "R3 passed is true but failures are listed" });
    if (!group.passed && group.failures.length === 0) errors.push({ at, message: "R3 passed is false but no failure is listed" });
  }
}

export function validate(changeSet) {
  const schema = loadSchema();
  const errors = [];
  check(schema, changeSet, "", schema, errors);
  rules(changeSet, errors);
  return errors.map((error) => `invalid ${error.at || "/"}: ${error.message}`);
}

function main(args) {
  if (args.length !== 1) {
    console.log("cannot validate: usage: node validate-changeset.mjs <file.json>");
    return 2;
  }
  let text;
  try {
    text = readFileSync(args[0], "utf8");
  } catch (error) {
    console.log(`cannot validate: cannot read ${args[0]}: ${error.message}`);
    return 2;
  }
  let changeSet;
  try {
    changeSet = JSON.parse(text);
  } catch (error) {
    console.log(`cannot validate: ${args[0]} is not JSON: ${error.message}`);
    return 2;
  }
  let lines;
  try {
    lines = validate(changeSet);
  } catch (error) {
    console.log(`cannot validate: ${error.message}`);
    return 2;
  }
  console.log(lines.length ? lines.join("\n") : "valid");
  return lines.length ? 1 : 0;
}

function runAsScript() {
  try {
    return Boolean(process.argv[1]) && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url));
  } catch {
    return false;
  }
}

if (runAsScript()) process.exitCode = main(process.argv.slice(2));
