import { describe, expect, it } from "vitest";

import { formatMoney, normalizeAmount } from "@/lib/money";

describe("formatMoney", () => {
  it("formats a whole-number decimal string to 2 dp", () => {
    expect(formatMoney("12")).toBe("$12.00");
  });

  it("formats a fractional decimal string to 2 dp", () => {
    expect(formatMoney("12.5")).toBe("$12.50");
  });

  it("keeps two decimal places as-is", () => {
    expect(formatMoney("25.00")).toBe("$25.00");
  });

  it("returns $0.00 for null, undefined, or empty input", () => {
    expect(formatMoney(null)).toBe("$0.00");
    expect(formatMoney(undefined)).toBe("$0.00");
    expect(formatMoney("")).toBe("$0.00");
    expect(formatMoney("   ")).toBe("$0.00");
  });

  it("returns $0.00 for non-numeric input instead of NaN", () => {
    expect(formatMoney("abc")).toBe("$0.00");
  });
});

describe("normalizeAmount", () => {
  it("normalizes valid positive input to a 2-decimal string", () => {
    expect(normalizeAmount("10")).toBe("10.00");
    expect(normalizeAmount("10.5")).toBe("10.50");
    expect(normalizeAmount(" 7.25 ")).toBe("7.25");
  });

  it("rejects zero and negative amounts", () => {
    expect(normalizeAmount("0")).toBeNull();
    expect(normalizeAmount("-5")).toBeNull();
  });

  it("rejects empty and non-numeric input", () => {
    expect(normalizeAmount("")).toBeNull();
    expect(normalizeAmount("abc")).toBeNull();
  });
});
