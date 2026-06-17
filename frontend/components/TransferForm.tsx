"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import type { UseMutationResult } from "@tanstack/react-query";

import { Button } from "@/components/Button";
import { normalizeAmount } from "@/lib/money";
import type { TransferInput, TransferResult } from "@/lib/types";

interface TransferFormProps {
  // "fund" | "spend" — selects the i18n namespace for labels.
  namespace: "fund" | "spend";
  mutation: UseMutationResult<TransferResult, Error, TransferInput>;
  onDone: (result: TransferResult) => void;
}

/**
 * Shared amount+note form for funding and spending. Validates the amount
 * client-side, then surfaces any backend error (e.g. insufficient balance)
 * verbatim to the user.
 */
export function TransferForm({
  namespace,
  mutation,
  onDone,
}: TransferFormProps) {
  const t = useTranslations(namespace);
  const tCommon = useTranslations("common");
  const [amount, setAmount] = useState("");
  const [note, setNote] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setValidationError(null);

    const normalized = normalizeAmount(amount);
    if (normalized === null) {
      setValidationError(t("amountError"));
      return;
    }

    const input: TransferInput = { amount: normalized };
    const trimmedNote = note.trim();
    if (trimmedNote) {
      input.note = trimmedNote;
    }

    try {
      const result = await mutation.mutateAsync(input);
      onDone(result);
    } catch {
      // Error message is rendered below from mutation.error.
    }
  }

  const serverError = mutation.error?.message ?? null;

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label
          htmlFor={`${namespace}-amount`}
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          {t("amountLabel")}
        </label>
        <input
          id={`${namespace}-amount`}
          type="number"
          inputMode="decimal"
          step="0.01"
          min="0"
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-piggy-500 focus:outline-none focus:ring-1 focus:ring-piggy-500"
          placeholder="0.00"
          autoFocus
        />
      </div>

      <div>
        <label
          htmlFor={`${namespace}-note`}
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          {t("noteLabel")}{" "}
          <span className="font-normal text-gray-400">
            ({tCommon("optional")})
          </span>
        </label>
        <input
          id={`${namespace}-note`}
          type="text"
          value={note}
          onChange={(event) => setNote(event.target.value)}
          className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-piggy-500 focus:outline-none focus:ring-1 focus:ring-piggy-500"
          placeholder={t("notePlaceholder")}
        />
      </div>

      {(validationError || serverError) && (
        <p role="alert" className="text-sm text-red-600">
          {validationError ?? serverError}
        </p>
      )}

      <Button type="submit" disabled={mutation.isPending} className="w-full">
        {mutation.isPending ? t("submitting") : t("submit")}
      </Button>
    </form>
  );
}
