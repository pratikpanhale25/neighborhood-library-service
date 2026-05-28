"use client";

import useSWR from "swr";
import Link from "next/link";
import { useState } from "react";
import { apiCreateBook, apiListBooks, ApiError } from "@/lib/api-client";
import { DataTable } from "@/components/DataTable";
import { FormDialog } from "@/components/FormDialog";
import { ListPaginationBar } from "@/components/ListPaginationBar";
import { goNextCursor, goPrevCursor, initialCursorNav, type CursorNav } from "@/lib/list-cursor-nav";
import { requireTrimmedNonEmpty } from "@/lib/form-validation";
import { useAsyncAction } from "@/lib/use-async-action";

const PAGE_SIZE = 25;

export default function BooksPage() {
  const [listNav, setListNav] = useState<CursorNav>(initialCursorNav);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [isbn, setIsbn] = useState("");
  const [copies, setCopies] = useState("1");
  const [formErr, setFormErr] = useState("");
  const { pending, run } = useAsyncAction();

  const { data, error, isLoading, mutate } = useSWR(
    ["books-list", listNav.cursor, PAGE_SIZE],
    () => apiListBooks({ page_size: PAGE_SIZE, page_token: listNav.cursor }),
  );

  const rows = data?.items ?? [];
  const errMsg =
    error instanceof ApiError
      ? error.body || error.message
      : error instanceof Error
        ? error.message
        : "";

  function openCreate() {
    setFormErr("");
    setTitle("");
    setAuthor("");
    setIsbn("");
    setCopies("1");
    setDialogOpen(true);
  }

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormErr("");

    // WHY: trim and reject empty strings server-side would still cost a round-trip; validate here first.
    const t = requireTrimmedNonEmpty(title, "Title");
    const a = requireTrimmedNonEmpty(author, "Author");
    const i = requireTrimmedNonEmpty(isbn, "Book number");
    if (!t.ok) {
      setFormErr(t.error);
      return;
    }
    if (!a.ok) {
      setFormErr(a.error);
      return;
    }
    if (!i.ok) {
      setFormErr(i.error);
      return;
    }

    await run(async () => {
      try {
        await apiCreateBook({
          title: t.value,
          author: a.value,
          isbn: i.value,
          total_copies: Math.max(1, parseInt(copies, 10) || 1),
        });
        setDialogOpen(false);
        await mutate();
      } catch (ex) {
        setFormErr(ex instanceof Error ? ex.message : "Create failed");
      }
    });
  }

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-2xl font-semibold text-zinc-900">Books</h1>
        <button
          type="button"
          className="rounded bg-zinc-900 px-3 py-1.5 text-sm text-white hover:bg-zinc-800"
          onClick={openCreate}
        >
          Add book
        </button>
      </div>

      <FormDialog
        open={dialogOpen}
        title="Add book"
        submitLabel="Create"
        pending={pending}
        onClose={() => !pending && setDialogOpen(false)}
        onSubmit={onCreate}
      >
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block">
            <span className="text-zinc-600">Title</span>
            <input
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-zinc-600">Author</span>
            <input
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-zinc-600">Book Number</span>
            <input
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={isbn}
              onChange={(e) => setIsbn(e.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-zinc-600">Total copies</span>
            <input
              type="number"
              min={1}
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={copies}
              onChange={(e) => setCopies(e.target.value)}
            />
          </label>
        </div>
        {formErr ? <p className="text-sm text-red-700">{formErr}</p> : null}
      </FormDialog>

      {errMsg ? (
        <p className="mb-2 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{errMsg}</p>
      ) : null}

      <ListPaginationBar
        disabled={isLoading}
        canPrevious={listNav.backStack.length > 0}
        canNext={Boolean(data?.next_page_token)}
        onPrevious={() => {
          const prev = goPrevCursor(listNav);
          if (prev) setListNav(prev);
        }}
        onNext={() => {
          const n = data?.next_page_token;
          if (n) setListNav((nav) => goNextCursor(nav, n));
        }}
      />

      <DataTable
        rowKey={(b) => b.id}
        emptyMessage="No books on this page."
        isLoading={isLoading}
        rows={rows}
        columns={[
          { header: "Title", cell: (b) => b.title },
          { header: "Author", cell: (b) => b.author },
          { header: "Book Number", cell: (b) => b.isbn },
          { header: "Copies", cell: (b) => b.total_copies },
          { header: "Available", cell: (b) => b.available_copies },
          {
            header: "",
            cell: (b) => (
              <Link href={`/books/${b.id}/edit`} className="text-blue-700 underline">
                Edit
              </Link>
            ),
          },
        ]}
      />
    </div>
  );
}
