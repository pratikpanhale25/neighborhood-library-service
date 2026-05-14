import { describe, expect, it } from "vitest";

import { normalizeOptionalTrimmed, requireTrimmedNonEmpty } from "./form-validation";

describe("requireTrimmedNonEmpty", () => {
  it("rejects whitespace-only input", () => {
    const r = requireTrimmedNonEmpty("   \t\n", "Title");
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error).toContain("Title");
  });

  it("returns trimmed value on success", () => {
    const r = requireTrimmedNonEmpty("  hello  ", "Title");
    expect(r).toEqual({ ok: true, value: "hello" });
  });
});

describe("normalizeOptionalTrimmed", () => {
  it("maps blank strings to null", () => {
    expect(normalizeOptionalTrimmed("")).toBeNull();
    expect(normalizeOptionalTrimmed("  ")).toBeNull();
  });

  it("returns trimmed non-empty strings", () => {
    expect(normalizeOptionalTrimmed("  x  ")).toBe("x");
  });
});
