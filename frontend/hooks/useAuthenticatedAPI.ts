"use client";

import { useCallback, useMemo } from "react";

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
 */
export function useAuthenticatedAPI() {
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
        return { data: null, error: "Network error. Is the backend running?" };
      }

      if (response.status === 401) {
        // Token is missing/invalid — drop it so the app can route to /login.
        clearToken();
        return { data: null, error: "Your session is invalid. Please log in again." };
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
          error: extractDetail(body, `Request failed (${response.status}).`),
        };
      }

      return { data: (body as T) ?? null, error: null };
    },
    [],
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
