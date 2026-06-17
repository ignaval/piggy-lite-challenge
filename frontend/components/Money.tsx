import { formatMoney } from "@/lib/money";

interface MoneyProps {
  amount: string | null | undefined;
  className?: string;
}

/** Display-only amount formatter (decimal string -> "$12.50"). */
export function Money({ amount, className }: MoneyProps) {
  return <span className={className}>{formatMoney(amount)}</span>;
}
