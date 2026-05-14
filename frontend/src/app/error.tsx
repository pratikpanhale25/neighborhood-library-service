"use client";

/**
 * WHY: Next.js route-level error boundaries catch unexpected render/client errors so a single
 * failure does not leave the user on a blank screen without a recovery action.
 */
export default function RootError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center p-6 text-zinc-900">
      <div className="max-w-md rounded-lg border border-red-200 bg-red-50 p-6 shadow-sm">
        <h1 className="text-lg font-semibold text-red-800">Something went wrong</h1>
        <p className="mt-2 text-sm text-zinc-700">{error.message}</p>
        <button
          type="button"
          className="mt-4 rounded bg-zinc-900 px-4 py-2 text-sm text-white hover:bg-zinc-800"
          onClick={() => reset()}
        >
          Try again
        </button>
      </div>
    </div>
  );
}
