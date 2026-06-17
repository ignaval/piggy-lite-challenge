// API contract types. Amounts are decimal STRINGS end-to-end (e.g. "10.00").

export type TransactionType = "FUNDING" | "SPEND";

export interface LedgerTransaction {
  id: string;
  type: TransactionType;
  amount: string;
  note: string | null;
  created_at: string;
}

export interface DependantSummary {
  id: string;
  first_name: string;
  balance: string;
}

export interface DependantDetail extends DependantSummary {
  transactions: LedgerTransaction[];
}

export interface TransferResult {
  transaction: LedgerTransaction;
  balance: string;
}

export interface TransferInput {
  amount: string;
  note?: string;
}
