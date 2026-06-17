// Money helpers. Backend sends/receives decimal STRINGS (2 dp). We never do
// floating-point math on balances here — we only format for display and
// normalize user input before sending it back as a string.

const CURRENCY_SYMBOL = "$";

/**
 * Format a decimal money string (e.g. "12.5") for display (e.g. "$12.50").
 * Falls back gracefully to "$0.00" for empty/invalid input so the UI never
 * renders "NaN".
 */
export function formatMoney(amount: string | null | undefined): string {
  if (amount === null || amount === undefined || amount.trim() === "") {
    return `${CURRENCY_SYMBOL}0.00`;
  }

  const parsed = Number(amount);
  if (!Number.isFinite(parsed)) {
    return `${CURRENCY_SYMBOL}0.00`;
  }

  const formatted = parsed.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return `${CURRENCY_SYMBOL}${formatted}`;
}

/**
 * Normalize raw user input ("10", "10.5", " 10.50 ") into a canonical
 * 2-decimal string ("10.00", "10.50") suitable for the API. Returns null when
 * the input is not a positive number, so callers can show a validation error.
 */
export function normalizeAmount(input: string): string | null {
  const trimmed = input.trim();
  if (trimmed === "") {
    return null;
  }

  const parsed = Number(trimmed);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return null;
  }

  return parsed.toFixed(2);
}
