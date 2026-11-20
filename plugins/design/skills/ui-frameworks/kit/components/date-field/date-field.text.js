// @ts-check
// The date field's text routines: how a language writes a date, and how typed text is read as one. They import only
// the calendar's date routines and touch no element, so the Web Component and every framework target read the same
// copy, and a server can load them (D113).
import { daysIn, iso } from '../calendar/calendar.dates.js';

/** @typedef {{ y: number, m: number, d: number }} Day */
/** @typedef {{ order: ('y' | 'm' | 'd')[], digits: string[] }} Layout  The field order and the ten digits of a language. */

/** A Date at midnight UTC of a day, any year from 1 to 9999. @param {number} y @param {number} m @param {number} d */
const utc = (y, m, d) => { const date = new Date(0); date.setUTCFullYear(y, m - 1, d); return date; };

/** @type {Map<string, Intl.DateTimeFormat>} */
const formatters = /* @__PURE__ */ new Map();
/** The formatter of a language: Gregorian, in UTC, numeric, with the language's own digits. @param {string} lang */
const formatter = (lang) => {
  let f = formatters.get(lang);
  if (!f) {
    f = new Intl.DateTimeFormat(lang, { calendar: 'gregory', year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'UTC' });
    formatters.set(lang, f);
  }
  return f;
};

/** @type {Map<string, Layout>} */
const layouts = /* @__PURE__ */ new Map();
/**
 * The field order and the digits of a language, from formatToParts of known dates: 2001-02-03 gives the order,
 * and the days 2001-01-01 to 2001-01-10, written in two digits, give the digits 1 to 9 and 0. No table of languages.
 * @param {string} lang @returns {Layout}
 */
export const layout = (lang) => {
  let l = layouts.get(lang);
  if (l) return l;
  const f = formatter(lang);
  const order = /** @type {('y' | 'm' | 'd')[]} */ (f.formatToParts(utc(2001, 2, 3)).map((p) => ({ year: 'y', month: 'm', day: 'd' })[/** @type {string} */ (p.type)]).filter(Boolean));
  const day = (/** @type {number} */ n) => [...(f.formatToParts(utc(2001, 1, n)).find((p) => p.type === 'day')?.value ?? '')];
  const digits = Array.from({ length: 10 }, (_, n) => (n === 0 ? day(10)[1] : day(n).at(-1)) ?? String(n));
  l = { order: order.length === 3 ? order : ['y', 'm', 'd'], digits };
  layouts.set(lang, l);
  return l;
};

/** A day as the language writes it, the year in four of its digits (date.year-literal). @param {string} lang @param {Day} day */
export const format = (lang, { y, m, d }) => {
  const zero = layout(lang).digits[0];
  return formatter(lang).formatToParts(utc(y, m, d)).map((p) => {
    if (p.type !== 'year') return p.value;
    const chars = [...p.value];
    return zero.repeat(Math.max(0, 4 - chars.length)) + p.value;
  }).join('');
};

/**
 * Reads typed text in a language's field order (J110). Returns '' for empty text, a yyyy-mm-dd for a whole date,
 * and null for anything else. The language's digits and ASCII digits are read; anything else separates. Three
 * groups of digits are the three fields; one group is eight digits, or six with a two-digit year. A year of one or
 * two digits falls in the hundred years around `year`; one of three or four is taken as written.
 * @param {string} lang @param {string} text @param {number} year @returns {string | null}
 */
export const read = (lang, text, year) => {
  const { order, digits } = layout(lang);
  const ascii = [...text].map((c) => { const n = digits.indexOf(c); return n >= 0 ? String(n) : c; }).join('');
  const groups = ascii.match(/\d+/g) ?? [];
  if (!groups.length) return ascii.trim() === '' ? '' : null;
  /** @type {Record<string, string>} */
  const at = {};
  if (groups.length === 3) order.forEach((field, n) => { at[field] = groups[n]; });
  else if (groups.length === 1 && (groups[0].length === 8 || groups[0].length === 6)) {
    let rest = groups[0];
    for (const field of order) {
      const take = field === 'y' ? groups[0].length - 4 : 2;
      at[field] = rest.slice(0, take);
      rest = rest.slice(take);
    }
  } else return null;
  let y = Number(at.y);
  if (at.y.length <= 2) {
    y += Math.floor(year / 100) * 100;
    if (y > year + 50) y -= 100;
    else if (y <= year - 50) y += 100;
  }
  const m = Number(at.m), d = Number(at.d);
  if (y < 1 || y > 9999 || m < 1 || m > 12 || d < 1 || d > daysIn(y, m)) return null;
  return iso({ y, m, d });
};

