export const locales = ["en", "es"] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = "en";

// Cookie used to persist the user's chosen locale (set by the LanguageSwitcher).
export const LOCALE_COOKIE = "PIGGY_LOCALE";

export function isLocale(value: string | undefined): value is Locale {
  return value !== undefined && (locales as readonly string[]).includes(value);
}
