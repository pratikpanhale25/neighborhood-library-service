"use client";

import type { FormEventHandler, ReactNode } from "react";

type FormDialogProps = {
  open: boolean;
  title: string;
  submitLabel: string;
  /** True while the async submit handler is in flight — disables buttons to block double submits. */
  pending: boolean;
  onClose: () => void;
  onSubmit: FormEventHandler<HTMLFormElement>;
  children: ReactNode;
};

/**
 * Reusable modal shell for **create and edit** flows so routes share one form UX (overlay, actions,
 * disabled state while pending) instead of duplicating markup.
 */
export function FormDialog({
  open,
  title,
  submitLabel,
  pending,
  onClose,
  onSubmit,
  children,
}: FormDialogProps) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="form-dialog-title"
    >
      <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-lg border border-zinc-200 bg-white p-4 shadow-lg">
        <div className="mb-4 flex items-center justify-between gap-2">
          <h2 id="form-dialog-title" className="text-lg font-semibold text-zinc-900">
            {title}
          </h2>
          <button
            type="button"
            className="rounded px-2 py-1 text-sm text-zinc-600 hover:bg-zinc-100"
            onClick={onClose}
            disabled={pending}
            aria-label="Close dialog"
          >
            ✕
          </button>
        </div>
        <form onSubmit={onSubmit} className="space-y-3 text-sm">
          {children}
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              className="rounded border border-zinc-300 px-3 py-1.5 hover:bg-zinc-50"
              onClick={onClose}
              disabled={pending}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded bg-zinc-900 px-3 py-1.5 text-white hover:bg-zinc-800 disabled:opacity-50"
              disabled={pending}
              aria-busy={pending}
            >
              {submitLabel}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
