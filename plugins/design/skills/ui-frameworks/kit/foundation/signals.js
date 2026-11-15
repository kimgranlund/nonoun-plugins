// @ts-check
/**
 * signals.js: the reactive kernel. It imports nothing.
 *
 * Surface: signal, computed, effect, scope, untracked, settled.
 * Rules: docs/specs/foundation.md, K1 to K11. There is no batch(): an effect runs once when it is
 * created, then at most once per microtask flush (D38).
 *
 * A write marks what depends on the signal. A read brings a computed up to date only if one of its
 * sources really changed, so an effect never sees a stale computed and never runs for an equal value.
 */

/** @type {number} Up to date. */
const CLEAN = 0;
/** @type {number} A source further up may have changed. */
const CHECK = 1;
/** @type {number} A direct source changed. */
const DIRTY = 2;

/**
 * @typedef {object} Node  One signal, computed or effect.
 * @property {(() => unknown) | null} f  The function of a computed or an effect; null for a signal.
 * @property {unknown} v  The current value.
 * @property {boolean} e  True for an effect.
 * @property {number} s  CLEAN, CHECK or DIRTY.
 * @property {Set<Node>} o  What reads this node.
 * @property {Set<Node> | null} d  What this node read in its last run.
 * @property {Set<Node> | null} t  What this node has read so far in the run in progress.
 * @property {(() => void) | undefined} c  The cleanup an effect's last run returned.
 * @property {Scope | null} w  The scope that owns this node.
 * @property {boolean} x  True once disposed.
 */

/**
 * @typedef {object} Scope  Owns every computed and effect created while it is active.
 * @property {string} [label]  Named in the error of a flush that does not settle.
 * @property {<T>(fn: () => T) => T} run  Makes the scope active for the length of fn.
 * @property {() => void} dispose  Disposes everything the scope owns.
 * @property {Node[]} _n  Internal: the owned nodes.
 */

/**
 * @template T
 * @typedef {{ value: T, peek(): T, readonly _n: Node }} Signal
 */
/**
 * @template T
 * @typedef {{ readonly value: T, peek(): T, readonly _n: Node }} Computed
 */

/** @type {Node | null} */
let current = null;
/** @type {Scope | null} */
let owner = null;
/** @type {Set<Node>} */
const queue = new Set();
/** @type {Promise<void> | null} */
let pending = null;
/** @type {(() => void) | null} */
let resolve = null;

/** @param {(() => unknown) | null} f @param {unknown} v @param {boolean} e @returns {Node} */
const node = (f, v, e) => {
  /** @type {Node} */
  const n = { f, v, e, s: f ? DIRTY : CLEAN, o: new Set(), d: null, t: null, c: undefined, w: owner, x: false };
  if (f && owner) owner._n.push(n);
  return n;
};

/** @param {unknown} error */
const report = (error) => {
  // @ts-ignore reportError exists in browsers; Node gets the fallback.
  if (typeof reportError === 'function') reportError(error);
  else setTimeout(() => { throw error; });
};

/** @param {Node} n */
function read(n) {
  if (n.t) throw new Error('signals: a computed read itself');
  if (current && current.t) current.t.add(n);
  if (n.f) update(n);
  return n.v;
}

/** Brings a computed or an effect up to date. @param {Node} n */
function update(n) {
  if (n.s === CHECK) {
    for (const source of /** @type {Set<Node>} */ (n.d)) {
      if (source.f) update(source);
      if (n.s === DIRTY) break;
    }
  }
  if (n.s === DIRTY) {
    // An effect is clean from the moment it starts, so a write it makes to its own source schedules it again.
    if (n.e) { n.s = CLEAN; run(n); return; }
    run(n);
  }
  n.s = CLEAN;
}

/** @param {Node} n */
function run(n) {
  const previous = current;
  const before = n.d;
  const now = (n.t = new Set());
  const cleanup = n.c;
  n.c = undefined;
  try {
    if (cleanup) { current = null; cleanup(); }
    current = n;
    const value = /** @type {() => unknown} */ (n.f)();
    if (n.e) n.c = typeof value === 'function' ? /** @type {() => void} */ (value) : undefined;
    else if (!Object.is(value, n.v)) {
      n.v = value;
      // Only a reader that is waiting to find out is told. One that is running now is reading the new value.
      for (const reader of n.o) if (reader.s === CHECK) reader.s = DIRTY;
    }
  } finally {
    current = previous;
    n.t = null;
    if (before) for (const source of before) if (!now.has(source)) source.o.delete(n);
    for (const source of now) source.o.add(n);
    n.d = now;
  }
}

/** @param {Node} n @param {number} state */
function mark(n, state) {
  if (n.s >= state) return;
  const was = n.s;
  n.s = state;
  if (was !== CLEAN) return;
  if (n.e) schedule(n);
  else for (const reader of n.o) mark(reader, CHECK);
}

/** @param {Node} n */
function schedule(n) {
  queue.add(n);
  if (!pending) {
    pending = new Promise((done) => { resolve = done; });
    queueMicrotask(flush);
  }
}

function flush() {
  let rounds = 0;
  try {
    while (queue.size) {
      const batch = [...queue];
      queue.clear();
      if (++rounds > 100) {
        for (const n of batch) n.s = CLEAN;
        report(new Error(`signals: effects were still writing after 100 rounds (owner: ${batch[0].w?.label ?? 'none'})`));
        break;
      }
      for (const n of batch) {
        if (n.x) continue;
        try { update(n); } catch (error) { report(error); }
      }
    }
  } finally {
    const done = resolve;
    pending = resolve = null;
    done?.();
  }
}

/** @param {Node} n */
function dispose(n) {
  n.x = true;
  queue.delete(n);
  if (n.d) for (const source of n.d) source.o.delete(n);
  n.d = null;
  const cleanup = n.c;
  n.c = undefined;
  if (cleanup) untracked(cleanup);
}

/**
 * A value that can be read and written.
 * @template T
 * @param {T} value
 * @returns {Signal<T>}
 */
export function signal(value) {
  const n = node(null, value, false);
  return {
    get value() { return /** @type {T} */ (read(n)); },
    set value(next) {
      if (Object.is(n.v, next)) return;
      n.v = next;
      for (const reader of n.o) mark(reader, DIRTY);
    },
    peek: () => /** @type {T} */ (n.v),
    _n: n,
  };
}

/**
 * A value derived from other values. It is computed when read, and only if a source changed.
 * @template T
 * @param {() => T} fn
 * @returns {Computed<T>}
 */
export function computed(fn) {
  const n = node(fn, undefined, false);
  return {
    get value() { return /** @type {T} */ (read(n)); },
    peek: () => untracked(() => /** @type {T} */ (read(n))),
    _n: n,
  };
}

/**
 * Runs fn now, and again after any value it read has changed. fn may return a cleanup function.
 * @param {() => void | (() => void)} fn
 * @returns {() => void} Stops the effect.
 */
export function effect(fn) {
  const n = node(fn, undefined, true);
  update(n);
  return () => dispose(n);
}

/**
 * A scope owns every computed and effect created inside run().
 * @param {string} [label]
 * @returns {Scope}
 */
export function scope(label) {
  /** @type {Scope} */
  const s = {
    label,
    _n: [],
    run(fn) {
      const previous = owner;
      owner = s;
      try { return fn(); } finally { owner = previous; }
    },
    dispose() { for (const n of s._n.splice(0)) dispose(n); },
  };
  return s;
}

/**
 * Runs fn without subscribing the effect or computed that is running.
 * @template T
 * @param {() => T} fn
 * @returns {T}
 */
export function untracked(fn) {
  const previous = current;
  current = null;
  try { return fn(); } finally { current = previous; }
}

/** Resolves once the effects that are waiting have run. @returns {Promise<void>} */
export const settled = () => pending ?? Promise.resolve();
