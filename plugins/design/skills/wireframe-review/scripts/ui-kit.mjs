import path from 'node:path';import * as api from './kit.mjs';
export const reviewRoot=path.resolve(import.meta.dirname,'..');
// The kit is local (scripts/kit.mjs); no sibling skill, lock or mirror is consulted.
export async function loadUI(){return {root:reviewRoot,api,identity:api.describeKit()};}
