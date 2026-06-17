"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

import { Button } from "@/components/Button";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { clearToken } from "@/lib/auth";

export function Header() {
  const t = useTranslations();
  const router = useRouter();

  function onLogout() {
    clearToken();
    router.replace("/login");
  }

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-2xl items-center justify-between px-4 py-3">
        <Link href="/" className="text-lg font-bold text-piggy-700">
          🐷 {t("app.title")}
        </Link>
        <div className="flex items-center gap-3">
          <LanguageSwitcher />
          <Button variant="secondary" onClick={onLogout}>
            {t("nav.logout")}
          </Button>
        </div>
      </div>
    </header>
  );
}
