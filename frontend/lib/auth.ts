// Auth seam. The token lives in localStorage under `piggy_token` and has the
// shape `guardian-{id}`. This mirrors real Piggy's `/test-login` dev seam — no
// Privy, no real secrets. The backend expects `Authorization: Bearer {token}`.

export const TOKEN_KEY = "piggy_token";

export function getToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(TOKEN_KEY);
}

/**
 * Accepts either a full token (`guardian-{id}`) or a bare guardian id and
 * stores the canonical `guardian-{id}` token. Trims whitespace.
 */
export function setToken(raw: string): void {
  if (typeof window === "undefined") {
    return;
  }
  const trimmed = raw.trim();
  const token = trimmed.startsWith("guardian-") ? trimmed : `guardian-${trimmed}`;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(TOKEN_KEY);
}
