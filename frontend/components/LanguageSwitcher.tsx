"use client";

import { useTransition } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useRouter } from "next/navigation";

import { locales, LOCALE_COOKIE, type Locale } from "@/i18n/config";

/** Persists the chosen locale in a cookie and refreshes server components. */
export function LanguageSwitcher() {
  const t = useTranslations("nav");
  const locale = useLocale();
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  function onChange(next: Locale) {
    // One year expiry; cookie is read in i18n/request.ts on the next render.
    document.cookie = `${LOCALE_COOKIE}=${next}; path=/; max-age=${60 * 60 * 24 * 365}`;
    startTransition(() => {
      router.refresh();
    });
  }

  return (
    <label className="flex items-center gap-1 text-sm text-gray-600">
      <span className="sr-only">{t("language")}</span>
      <select
        value={locale}
        disabled={isPending}
        onChange={(event) => onChange(event.target.value as Locale)}
        className="rounded border border-gray-300 bg-white px-2 py-1"
      >
        {locales.map((loc) => (
          <option key={loc} value={loc}>
            {loc.toUpperCase()}
          </option>
        ))}
      </select>
    </label>
  );
}
