"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { useAuthenticatedAPI } from "@/hooks/useAuthenticatedAPI";
import type {
  DependantDetail,
  DependantSummary,
  TransferInput,
  TransferResult,
} from "@/lib/types";

// Query keys live in one place so mutations can invalidate precisely.
export const dependantKeys = {
  all: ["dependants"] as const,
  detail: (id: string) => ["dependants", id] as const,
};

/** GET /dependants — the current guardian's dependants with balances. */
export function useDependants() {
  const api = useAuthenticatedAPI();
  return useQuery({
    queryKey: dependantKeys.all,
    queryFn: async () => {
      const { data, error } = await api.get<DependantSummary[]>("/dependants");
      if (error) {
        throw new Error(error);
      }
      return data ?? [];
    },
  });
}

/** GET /dependants/{id} — balance + recent transactions. */
export function useDependant(id: string) {
  const api = useAuthenticatedAPI();
  return useQuery({
    queryKey: dependantKeys.detail(id),
    queryFn: async () => {
      const { data, error } = await api.get<DependantDetail>(`/dependants/${id}`);
      if (error) {
        throw new Error(error);
      }
      return data;
    },
    enabled: Boolean(id),
  });
}

/** Shared mutation factory for fund/spend so invalidation stays consistent. */
function useTransferMutation(
  action: "fund" | "spend",
  dependantId: string,
) {
  const api = useAuthenticatedAPI();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: TransferInput) => {
      const { data, error } = await api.post<TransferResult>(
        `/dependants/${dependantId}/${action}`,
        input,
      );
      if (error) {
        // Surface the backend's typed message (e.g. insufficient balance).
        throw new Error(error);
      }
      return data as TransferResult;
    },
    onSuccess: () => {
      // Balances changed: refresh both the list and this dependant's detail.
      queryClient.invalidateQueries({ queryKey: dependantKeys.all });
      queryClient.invalidateQueries({
        queryKey: dependantKeys.detail(dependantId),
      });
    },
  });
}

/** POST /dependants/{id}/fund */
export function useFund(dependantId: string) {
  return useTransferMutation("fund", dependantId);
}

/** POST /dependants/{id}/spend */
export function useSpend(dependantId: string) {
  return useTransferMutation("spend", dependantId);
}
