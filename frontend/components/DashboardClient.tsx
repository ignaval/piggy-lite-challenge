"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";

import { FundButton } from "@/components/FundButton";
import { Money } from "@/components/Money";
import { useDependants } from "@/hooks/useDependants";

export function DashboardClient() {
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const { data, isLoading, isError } = useDependants();

  return (
    <section>
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("title")}</h1>
        <p className="text-sm text-gray-500">{t("subtitle")}</p>
      </header>

      {isLoading && <p className="text-gray-500">{tCommon("loading")}</p>}

      {isError && (
        <p role="alert" className="text-red-600">
          {t("loadError")}
        </p>
      )}

      {!isLoading && !isError && data && data.length === 0 && (
        <p className="text-gray-500">{t("empty")}</p>
      )}

      {!isLoading && !isError && data && data.length > 0 && (
        <ul className="space-y-3">
          {data.map((dependant) => (
            <li
              key={dependant.id}
              className="rounded-lg border border-gray-200 bg-white p-4"
              data-testid="dependant-card"
            >
              <div className="flex items-center justify-between gap-4">
                <div>
                  <Link
                    href={`/dependants/${dependant.id}`}
                    className="text-lg font-semibold text-gray-900 hover:text-piggy-700"
                  >
                    {dependant.first_name}
                  </Link>
                  <p className="text-sm text-gray-500">
                    {t("balance")}:{" "}
                    <Money
                      amount={dependant.balance}
                      className="font-medium text-gray-900"
                    />
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Link
                    href={`/dependants/${dependant.id}`}
                    className="text-sm font-medium text-piggy-700 hover:underline"
                  >
                    {t("view")}
                  </Link>
                  <FundButton dependant={dependant} />
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
