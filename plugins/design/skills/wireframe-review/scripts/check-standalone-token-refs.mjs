// Compatibility entry; base-ui owns this check.
export {inspectStyles} from './token-inspection.mjs';
import {runUICheck} from './run-ui-check.mjs';
await runUICheck('check-standalone-token-refs.mjs');
