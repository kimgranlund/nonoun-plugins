// @ts-check
// The calendar's date routines: plain year, month and day numbers of the proleptic Gregorian calendar, with no Date
// arithmetic that a time zone could shift. They import nothing and touch no element, so the Web Component and every
// framework target read the same copy, and a server can load them (D113).

/** @typedef {{ y: number, m: number, d: number }} Day  A day of the proleptic Gregorian calendar. */

/** Whether a year is a leap year. @param {number} y */
export const leap = (y) => y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
/** The number of days in a month. @param {number} y @param {number} m */
export const daysIn = (y, m) => (m === 2 ? (leap(y) ? 29 : 28) : [4, 6, 9, 11].includes(m) ? 30 : 31);

/** The days from 1970-01-01 to a day: H. Hinnant's days_from_civil, in integers. @param {Day} day */
export const serial = ({ y, m, d }) => {
  const year = m <= 2 ? y - 1 : y;
  const era = Math.floor(year / 400);
  const yoe = year - era * 400;
  const doy = Math.floor((153 * (m + (m > 2 ? -3 : 9)) + 2) / 5) + d - 1;
  return era * 146097 + yoe * 365 + Math.floor(yoe / 4) - Math.floor(yoe / 100) + doy - 719468;
};
/** The day a count of days from 1970-01-01 lands on: civil_from_days. @param {number} n @returns {Day} */
export const fromSerial = (n) => {
  const z = n + 719468;
  const era = Math.floor(z / 146097);
  const doe = z - era * 146097;
  const yoe = Math.floor((doe - Math.floor(doe / 1460) + Math.floor(doe / 36524) - Math.floor(doe / 146096)) / 365);
  const doy = doe - (365 * yoe + Math.floor(yoe / 4) - Math.floor(yoe / 100));
  const mp = Math.floor((5 * doy + 2) / 153);
  const m = mp < 10 ? mp + 3 : mp - 9;
  return { y: yoe + era * 400 + (m <= 2 ? 1 : 0), m, d: doy - Math.floor((153 * mp + 2) / 5) + 1 };
};
/** The weekday of a count of days, 0 for Sunday: 1970-01-01 was a Thursday. @param {number} n */
export const weekday = (n) => (((n + 4) % 7) + 7) % 7;

/**
 * The first and the last day the calendar can show (date.bounds): serial() of 0001-01-01 and of 9999-12-31, written
 * as numbers so that importing this module runs no code (R1); calendar.zones.test.js holds them to serial().
 */
export const FIRST = -719162;
export const LAST = 2932896;

/** A day as yyyy-mm-dd, the year in four digits. @param {Day} day */
export const iso = ({ y, m, d }) => `${String(y).padStart(4, '0')}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
/** The day a yyyy-mm-dd text names, or null when it names none (date.value-format). @param {string | null | undefined} text */
export const parseDate = (text) => {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(text ?? '');
  if (!match) return null;
  const [y, m, d] = match.slice(1).map(Number);
  return y >= 1 && m >= 1 && m <= 12 && d >= 1 && d <= daysIn(y, m) ? { y, m, d } : null;
};
/** The month a yyyy-mm text names, or null. @param {string | null | undefined} text @returns {{ y: number, m: number } | null} */
export const parseMonth = (text) => {
  const match = /^(\d{4})-(\d{2})$/.exec(text ?? '');
  if (!match) return null;
  const [y, m] = match.slice(1).map(Number);
  return y >= 1 && m >= 1 && m <= 12 ? { y, m } : null;
};
/** The same day some months later or earlier, or the last day of that month; null past the years 0001 to 9999. @param {Day} day @param {number} by */
export const addMonths = ({ y, m, d }, by) => {
  const total = y * 12 + (m - 1) + by;
  const year = Math.floor(total / 12), month = (total % 12) + 1;
  return year < 1 || year > 9999 ? null : { y: year, m: month, d: Math.min(d, daysIn(year, month)) };
};

/**
 * The regions whose week does not start on Monday, by the first day (0 Sunday, 5 Friday, 6 Saturday), from the
 * CLDR week data in ICU 77. Read only where the engine has no week information, as in Firefox (date.week-start).
 */
const WEEK = {
  5: 'MV',
  6: 'AF BH DJ DZ EG IQ IR JO KW LY OM QA SD SY',
  0: 'AG AS BD BR BS BT BW BZ CA CO DM DO ET GT GU HK HN ID IL IN IS JM JP KE KH KR LA MH MM MO MT MX MZ NI NP PA PE PH PK PR PT PY SA SG SV TH TT TW UM US VE VI WS YE ZA ZW',
};
/** The first day of the week for a language, 0 for Sunday. @param {string} lang */
export const weekStart = (lang) => {
  try {
    const locale = /** @type {any} */ (new Intl.Locale(lang));
    const info = typeof locale.getWeekInfo === 'function' ? locale.getWeekInfo() : locale.weekInfo;
    if (info && Number.isInteger(info.firstDay)) return info.firstDay % 7;
    const region = locale.maximize().region ?? '';
    for (const [day, list] of Object.entries(WEEK)) if (list.split(' ').includes(region)) return Number(day);
  } catch { /* a language the engine cannot read starts on Monday */ }
  return 1;
};

/** A Date at midnight UTC of a day, any year from 1 to 9999 included. @param {number} y @param {number} m @param {number} d */
const utc = (y, m, d) => { const date = new Date(0); date.setUTCFullYear(y, m - 1, d); return date; };
/** A day formatted in the Gregorian calendar, in UTC (date.gregorian). @param {string} lang @param {Intl.DateTimeFormatOptions} options @param {number} y @param {number} m @param {number} d */
export const format = (lang, options, y, m, d) => new Intl.DateTimeFormat(lang, { calendar: 'gregory', timeZone: 'UTC', ...options }).format(utc(y, m, d));
