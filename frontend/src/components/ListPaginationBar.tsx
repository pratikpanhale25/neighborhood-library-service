"use client";

type ListPaginationBarProps = {
  onPrevious: () => void;
  onNext: () => void;
  canPrevious: boolean;
  canNext: boolean;
  disabled?: boolean;
};

/** Cursor list navigation: stack of tokens is owned by the parent; this bar only fires events. */
export function ListPaginationBar({
  onPrevious,
  onNext,
  canPrevious,
  canNext,
  disabled,
}: ListPaginationBarProps) {
  return (
    <div className="mb-2 flex items-center justify-end gap-2">
      <button
        type="button"
        className="rounded border border-zinc-300 px-3 py-1 text-sm hover:bg-zinc-50 disabled:opacity-50"
        onClick={onPrevious}
        disabled={disabled || !canPrevious}
      >
        Previous
      </button>
      <button
        type="button"
        className="rounded border border-zinc-300 px-3 py-1 text-sm hover:bg-zinc-50 disabled:opacity-50"
        onClick={onNext}
        disabled={disabled || !canNext}
      >
        Next
      </button>
    </div>
  );
}
