"use client";

import { useFormatter, useTranslations } from "next-intl";

import { Money } from "@/components/Money";
import type { LedgerTransaction } from "@/lib/types";

export function TransactionList({
  transactions,
}: {
  transactions: LedgerTransaction[];
}) {
  const t = useTranslations("dependant");
  const tType = useTranslations("transaction.type");
  const format = useFormatter();

  if (transactions.length === 0) {
    return <p className="text-gray-500">{t("noTransactions")}</p>;
  }

  return (
    <ul className="divide-y divide-gray-100" data-testid="transaction-list">
      {transactions.map((tx) => {
        const isFunding = tx.type === "FUNDING";
        return (
          <li key={tx.id} className="flex items-center justify-between py-3">
            <div>
              <p className="font-medium text-gray-900">{tType(tx.type)}</p>
              {tx.note && (
                <p className="text-sm text-gray-500">{tx.note}</p>
              )}
              <p className="text-xs text-gray-400">
                {format.dateTime(new Date(tx.created_at), {
                  dateStyle: "medium",
                  timeStyle: "short",
                })}
              </p>
            </div>
            <span
              className={
                isFunding
                  ? "font-semibold text-green-600"
                  : "font-semibold text-gray-900"
              }
            >
              {isFunding ? "+" : "−"}
              <Money amount={tx.amount} />
            </span>
          </li>
        );
      })}
    </ul>
  );
}
