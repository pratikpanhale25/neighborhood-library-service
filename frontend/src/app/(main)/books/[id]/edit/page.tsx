"use client";

import useSWR from "swr";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { apiGetBook, apiUpdateBook, ApiError } from "@/lib/api-client";
import { FormDialog } from "@/components/FormDialog";
import { requireTrimmedNonEmpty } from "@/lib/form-validation";
import { useAsyncAction } from "@/lib/use-async-action";

export default function EditBookPage() {
  const params = useParams();
  const id = String(params.id ?? "");
  const router = useRouter();
  const { data, error, isLoading } = useSWR(id ? ["book", id] : null, () => apiGetBook(id));
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [isbn, setIsbn] = useState("");
  const [total, setTotal] = useState("");
  const [year, setYear] = useState("");
  const [msg, setMsg] = useState("");
  const { pending, run } = useAsyncAction();

  useEffect(() => {
    if (!data) return;
    setTitle(data.title);
    setAuthor(data.author);
    setIsbn(data.isbn);
    setTotal(String(data.total_copies));
    setYear(data.publication_year != null ? String(data.publication_year) : "");
  }, [data]);

  function handleClose() {
    router.push("/books");
  }

  async function onSave(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");

    const t = requireTrimmedNonEmpty(title, "Title");
    const a = requireTrimmedNonEmpty(author, "Author");
    const i = requireTrimmedNonEmpty(isbn, "Book number");
    const tot = requireTrimmedNonEmpty(total, "Total copies");
    if (!t.ok) {
      setMsg(t.error);
      return;
    }
    if (!a.ok) {
      setMsg(a.error);
      return;
    }
    if (!i.ok) {
      setMsg(i.error);
      return;
    }
    if (!tot.ok) {
      setMsg(tot.error);
      return;
    }
    const totalNum = parseInt(tot.value, 10);
    if (Number.isNaN(totalNum) || totalNum < 1) {
      setMsg("Total copies must be at least 1.");
      return;
    }

    await run(async () => {
      try {
        await apiUpdateBook(id, {
          title: t.value,
          author: a.value,
          isbn: i.value,
          publication_year: year.trim() ? parseInt(year.trim(), 10) : null,
          total_copies: totalNum,
        });
        router.push("/books");
      } catch (ex) {
        setMsg(ex instanceof ApiError ? ex.body || ex.message : "Save failed");
      }
    });
  }

  if (isLoading) return <p className="text-sm text-zinc-600">Loading…</p>;
  if (error)
    return (
      <p className="text-sm text-red-700">
        {error instanceof ApiError ? error.body || error.message : "Error"}
      </p>
    );

  // WHY: Reuse FormDialog for edit so Create/Edit share the same modal shell and behavior as list create.
  return (
    <FormDialog
      open={Boolean(data)}
      title="Edit book"
      submitLabel="Save"
      pending={pending}
      onClose={handleClose}
      onSubmit={onSave}
    >
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block sm:col-span-2">
          <span className="text-zinc-600">Title</span>
          <input
            className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </label>
        <label className="block sm:col-span-2">
          <span className="text-zinc-600">Author</span>
          <input
            className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
          />
        </label>
        <label className="block sm:col-span-2">
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
            value={total}
            onChange={(e) => setTotal(e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-zinc-600">Publication year</span>
          <input
            className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
            value={year}
            onChange={(e) => setYear(e.target.value)}
          />
        </label>
      </div>
      {msg ? <p className="text-sm text-red-700">{msg}</p> : null}
    </FormDialog>
  );
}
