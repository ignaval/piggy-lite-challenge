import { cookies } from "next/headers";
import { getRequestConfig } from "next-intl/server";

import { defaultLocale, isLocale, LOCALE_COOKIE } from "./config";

// next-intl reads the active locale per request. We keep routing simple (no
// /[locale] segment) and instead persist the choice in a cookie that the
// LanguageSwitcher writes.
export default getRequestConfig(async () => {
  const cookieStore = await cookies();
  const cookieLocale = cookieStore.get(LOCALE_COOKIE)?.value;
  const locale = isLocale(cookieLocale) ? cookieLocale : defaultLocale;

  return {
    locale,
    messages: (await import(`./locales/${locale}.json`)).default,
  };
});
