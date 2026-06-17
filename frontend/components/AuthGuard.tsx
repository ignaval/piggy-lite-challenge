"use client";

import { useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

import { getToken } from "@/lib/auth";

/**
 * Client-side route guard. The token lives in localStorage, so we check it
 * after mount and redirect to /login when absent. Renders nothing until the
 * check completes to avoid flashing protected content.
 */
export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const t = useTranslations("common");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (getToken()) {
      setReady(true);
    } else {
      router.replace("/login");
    }
  }, [router]);

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center text-gray-500">
        {t("loading")}
      </div>
    );
  }

  return <>{children}</>;
}
