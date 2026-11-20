// Finds a file of a sibling skill (ui-colors, ui-geometry, ui-materials) for the scripts that read one.
//
//   import { sibling } from './siblings.mjs';
//   sibling('ui-geometry/scripts/derive.mjs')   the absolute path of that file in the first folder that has it
//
// The folders are tried in this order: the one SKILLS_DIR names, when set; the folder that holds this skill
// (a plugin install keeps the siblings there); ~/.claude/skills. When none has the file, the error names each
// place tried.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));

/** The folders a sibling skill is looked up in, in order, without repeats. */
export function skillDirs() {
  const dirs = [];
  if (process.env.SKILLS_DIR) dirs.push(path.resolve(process.env.SKILLS_DIR));
  dirs.push(path.resolve(here, '../..'));
  dirs.push(path.join(os.homedir(), '.claude/skills'));
  return [...new Set(dirs)];
}

/** The absolute path of `rel` (a path that starts with the sibling skill's name) in the first folder that has it. */
export function sibling(rel) {
  const tried = skillDirs().map((dir) => path.join(dir, rel));
  const found = tried.find((file) => fs.existsSync(file));
  if (found) return found;
  throw new Error(`cannot find the sibling skill file ${rel}; tried:\n${tried.map((file) => `  ${file}`).join('\n')}\nInstall the sibling skill beside this one or in ~/.claude/skills, or set SKILLS_DIR to the folder that holds it.`);
}
