"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

import { Button } from "@/components/Button";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const t = useTranslations("login");
  const tApp = useTranslations("app");
  const router = useRouter();
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (value.trim() === "") {
      setError(t("emptyError"));
      return;
    }
    setToken(value);
    router.replace("/");
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-piggy-50 px-4">
      <div className="absolute right-4 top-4">
        <LanguageSwitcher />
      </div>
      <div className="w-full max-w-sm rounded-xl bg-white p-8 shadow-sm">
        <div className="mb-6 text-center">
          <div className="text-4xl">🐷</div>
          <h1 className="mt-2 text-xl font-bold text-gray-900">
            {tApp("title")}
          </h1>
          <p className="text-sm text-gray-500">{tApp("tagline")}</p>
        </div>

        <h2 className="mb-2 text-lg font-semibold text-gray-900">
          {t("title")}
        </h2>
        <p className="mb-4 text-sm text-gray-600">{t("description")}</p>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="token"
              className="mb-1 block text-sm font-medium text-gray-700"
            >
              {t("tokenLabel")}
            </label>
            <input
              id="token"
              type="text"
              value={value}
              onChange={(event) => setValue(event.target.value)}
              placeholder={t("tokenPlaceholder")}
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-piggy-500 focus:outline-none focus:ring-1 focus:ring-piggy-500"
              autoFocus
            />
          </div>

          {error && (
            <p role="alert" className="text-sm text-red-600">
              {error}
            </p>
          )}

          <Button type="submit" className="w-full">
            {t("submit")}
          </Button>
        </form>

        <p className="mt-4 text-xs text-gray-400">{t("hint")}</p>
      </div>
    </main>
  );
}
