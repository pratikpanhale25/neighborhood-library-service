"use client";

/**
 * WHY: Isolates staff-route failures from the rest of the tree so nav chrome can still recover
 * via reset() without forcing a full document reload for unrelated segments.
 */
export default function MainSegmentError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">
      <p className="font-medium">This page hit an error.</p>
      <p className="mt-1 text-amber-900/90">{error.message}</p>
      <button
        type="button"
        className="mt-3 rounded border border-amber-800/30 bg-white px-3 py-1.5 text-amber-950 hover:bg-amber-100"
        onClick={() => reset()}
      >
        Try again
      </button>
    </div>
  );
}
