"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";

import { Money } from "@/components/Money";
import { SpendButton } from "@/components/SpendButton";
import { TransactionList } from "@/components/TransactionList";
import { useDependant } from "@/hooks/useDependants";

export function DependantDetailClient({ id }: { id: string }) {
  const t = useTranslations("dependant");
  const tNav = useTranslations("nav");
  const tCommon = useTranslations("common");
  const { data, isLoading, isError } = useDependant(id);

  if (isLoading) {
    return <p className="text-gray-500">{tCommon("loading")}</p>;
  }

  if (isError || !data) {
    return (
      <div className="space-y-4">
        <p role="alert" className="text-red-600">
          {t("loadError")}
        </p>
        <Link href="/" className="text-sm text-piggy-700 hover:underline">
          ← {tNav("back")}
        </Link>
      </div>
    );
  }

  return (
    <section className="space-y-6">
      <Link href="/" className="text-sm text-piggy-700 hover:underline">
        ← {tNav("back")}
      </Link>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {data.first_name}
            </h1>
            <p className="mt-1 text-sm text-gray-500">{t("balance")}</p>
            <Money
              amount={data.balance}
              className="text-3xl font-bold text-gray-900"
            />
          </div>
          <SpendButton dependantId={data.id} dependantName={data.first_name} />
        </div>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <h2 className="mb-3 text-lg font-semibold text-gray-900">
          {t("history")}
        </h2>
        <TransactionList transactions={data.transactions} />
      </div>
    </section>
  );
}
