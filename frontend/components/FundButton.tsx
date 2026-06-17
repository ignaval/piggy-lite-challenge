"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

import { Button } from "@/components/Button";
import { Modal } from "@/components/Modal";
import { TransferForm } from "@/components/TransferForm";
import { useFund } from "@/hooks/useDependants";
import type { DependantSummary } from "@/lib/types";

/** "Send funds" action + modal for a single dependant on the dashboard. */
export function FundButton({ dependant }: { dependant: DependantSummary }) {
  const t = useTranslations("fund");
  const tDashboard = useTranslations("dashboard");
  const [open, setOpen] = useState(false);
  const mutation = useFund(dependant.id);

  function close() {
    setOpen(false);
    mutation.reset();
  }

  return (
    <>
      <Button onClick={() => setOpen(true)}>{tDashboard("sendFunds")}</Button>
      <Modal
        open={open}
        title={t("title", { name: dependant.first_name })}
        onClose={close}
      >
        <TransferForm namespace="fund" mutation={mutation} onDone={close} />
      </Modal>
    </>
  );
}
