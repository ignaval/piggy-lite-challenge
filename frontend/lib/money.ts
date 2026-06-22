// Money helpers. Backend sends/receives decimal STRINGS (2 dp). We never do
// floating-point math on balances here — we format for display and normalize
// user input (via string rules, not floats) before sending it back as a string.

const CURRENCY_SYMBOL = "$";

/**
 * Format a money string from the API (e.g. "12.5") for display (e.g. "$12.50").
 * Display-only: the input is a trusted 2-dp string from the backend, so using
 * Number() purely for locale grouping here is safe. Falls back to "$0.00" for
 * empty/invalid input so the UI never renders "NaN".
 */
export function formatMoney(amount: string | null | undefined): string {
  if (amount === null || amount === undefined || amount.trim() === "") {
    return `${CURRENCY_SYMBOL}0.00`;
  }

  const parsed = Number(amount);
  if (!Number.isFinite(parsed)) {
    return `${CURRENCY_SYMBOL}0.00`;
  }

  // Pin the locale (rather than the runtime default) so output is deterministic
  // across machines, server vs. client render (no hydration drift), and CI.
  // Piggy Lite is single-currency USD, so display is intentionally
  // locale-independent; a multi-currency app would format per active locale and
  // per asset via Intl.NumberFormat.
  const formatted = parsed.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return `${CURRENCY_SYMBOL}${formatted}`;
}

/**
 * Normalize raw user input ("10", "10.5", " 10.50 ") into a canonical
 * 2-decimal string ("10.00", "10.50") for the API — using string/regex rules,
 * never floating-point math. Returns null when the input is not a positive
 * number with at most 2 decimal places, so callers can show a validation error.
 *
 * Rejecting >2 dp (rather than silently rounding, which `Number(x).toFixed(2)`
 * does — e.g. "1.005" → "1.00") keeps money exact and matches the backend,
 * which also rejects sub-cent amounts.
 */
export function normalizeAmount(input: string): string | null {
  const trimmed = input.trim();

  // digits, optional single dot followed by 1–2 fractional digits
  if (!/^\d+(\.\d{1,2})?$/.test(trimmed)) {
    return null;
  }
  // must be strictly greater than zero
  if (/^0+(\.0{1,2})?$/.test(trimmed)) {
    return null;
  }

  const [whole, frac = ""] = trimmed.split(".");
  const cents = `${frac}00`.slice(0, 2);
  const normalizedWhole = whole.replace(/^0+(?=\d)/, "");
  return `${normalizedWhole}.${cents}`;
}
