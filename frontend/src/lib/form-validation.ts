/**
 * Form validation helpers for staff UI submits.
 *
 * WHY: Native HTML `required` (and `type="email"`) still accepts whitespace-only
 * strings as non-empty, so users can accidentally send meaningless data to the API.
 */

export type TrimmedOk = { ok: true; value: string };
export type TrimmedErr = { ok: false; error: string };
export type TrimmedResult = TrimmedOk | TrimmedErr;

/** Require a non-empty string after trim; returns the trimmed value on success. */
export function requireTrimmedNonEmpty(raw: string, fieldLabel: string): TrimmedResult {
  const value = raw.trim();
  if (!value) {
    return { ok: false, error: `${fieldLabel} is required.` };
  }
  return { ok: true, value };
}

/** Optional field: empty or whitespace-only becomes null; otherwise trimmed string. */
export function normalizeOptionalTrimmed(raw: string): string | null {
  const value = raw.trim();
  return value.length > 0 ? value : null;
}
