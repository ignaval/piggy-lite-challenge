"use client";

import { useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

import { clearToken, getToken } from "@/lib/auth";

export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_PREFIX = "/api/v1";

/** Pull a human-readable message out of a FastAPI error body, if present. */
function extractDetail(body: unknown, fallback: string): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    // FastAPI validation errors arrive as a list of {msg, loc, ...}.
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0];
      if (first && typeof first === "object" && "msg" in first) {
        const msg = (first as { msg: unknown }).msg;
        if (typeof msg === "string") {
          return msg;
        }
      }
    }
  }
  return fallback;
}

/**
 * Centralized authenticated fetch wrapper. Reads the token from localStorage on
 * each call, prefixes `/api/v1`, and returns a typed `{ data, error }` instead
 * of throwing — callers (and React Query hooks) branch on `error`.
 *
 * The wrapper's own user-facing messages (network / session / fallback) are
 * translated via the `errors` i18n namespace. Backend error `detail` strings
 * are surfaced verbatim and treated as developer-facing (see the README) — if
 * you want them localized, map error codes to i18n keys client-side.
 */
export function useAuthenticatedAPI() {
  const t = useTranslations("errors");
  const router = useRouter();
  const request = useCallback(
    async <T>(
      path: string,
      init?: RequestInit,
    ): Promise<ApiResponse<T>> => {
      const token = getToken();
      const headers = new Headers(init?.headers);
      headers.set("Content-Type", "application/json");
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }

      let response: Response;
      try {
        response = await fetch(`${API_BASE}${API_PREFIX}${path}`, {
          ...init,
          headers,
        });
      } catch {
        return { data: null, error: t("network") };
      }

      if (response.status === 401) {
        // Token is missing/invalid — drop it and bounce to /login instead of
        // leaving the user on a protected page showing a generic error.
        clearToken();
        router.replace("/login");
        return { data: null, error: t("session") };
      }

      let body: unknown = null;
      const text = await response.text();
      if (text) {
        try {
          body = JSON.parse(text);
        } catch {
          body = null;
        }
      }

      if (!response.ok) {
        return {
          data: null,
          error: extractDetail(
            body,
            t("requestFailed", { status: response.status }),
          ),
        };
      }

      return { data: (body as T) ?? null, error: null };
    },
    [t, router],
  );

  const get = useCallback(
    <T>(path: string) => request<T>(path, { method: "GET" }),
    [request],
  );

  const post = useCallback(
    <T>(path: string, payload?: unknown) =>
      request<T>(path, {
        method: "POST",
        body: payload === undefined ? undefined : JSON.stringify(payload),
      }),
    [request],
  );

  return useMemo(() => ({ get, post }), [get, post]);
}
