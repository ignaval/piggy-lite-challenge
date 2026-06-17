"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

import { Button } from "@/components/Button";
import { Modal } from "@/components/Modal";
import { TransferForm } from "@/components/TransferForm";
import { useSpend } from "@/hooks/useDependants";

interface SpendButtonProps {
  dependantId: string;
  dependantName: string;
}

/** "Spend" action + modal on the dependant detail page (records a SPEND). */
export function SpendButton({ dependantId, dependantName }: SpendButtonProps) {
  const t = useTranslations("spend");
  const [open, setOpen] = useState(false);
  const mutation = useSpend(dependantId);

  function close() {
    setOpen(false);
    mutation.reset();
  }

  return (
    <>
      <Button onClick={() => setOpen(true)}>{t("submit")}</Button>
      <Modal
        open={open}
        title={t("title", { name: dependantName })}
        onClose={close}
      >
        <TransferForm namespace="spend" mutation={mutation} onDone={close} />
      </Modal>
    </>
  );
}
