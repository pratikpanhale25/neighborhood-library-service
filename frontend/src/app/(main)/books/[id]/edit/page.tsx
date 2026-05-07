"use client";

import useSWR from "swr";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { apiGetBook, apiUpdateBook, ApiError } from "@/lib/api-client";

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

  useEffect(() => {
    if (!data) return;
    setTitle(data.title);
    setAuthor(data.author);
    setIsbn(data.isbn);
    setTotal(String(data.total_copies));
    setYear(data.publication_year != null ? String(data.publication_year) : "");
  }, [data]);

  async function onSave(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");
    try {
      await apiUpdateBook(id, {
        title,
        author,
        isbn,
        publication_year: year ? parseInt(year, 10) : null,
        total_copies: total ? parseInt(total, 10) : null,
      });
      router.push("/books");
    } catch (ex) {
      setMsg(ex instanceof ApiError ? ex.body || ex.message : "Save failed");
    }
  }

  if (isLoading) return <p className="text-sm text-zinc-600">Loading…</p>;
  if (error)
    return (
      <p className="text-sm text-red-700">
        {error instanceof ApiError ? error.body || error.message : "Error"}
      </p>
    );

  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold text-zinc-900">Edit book</h1>
      <form onSubmit={onSave} className="max-w-lg space-y-3 text-sm">
        <label className="block">
          <span className="text-zinc-600">Title</span>
          <input
            className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </label>
        <label className="block">
          <span className="text-zinc-600">Author</span>
          <input
            className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            required
          />
        </label>
        <label className="block">
          <span className="text-zinc-600">Book Number</span>
          <input
            className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
            value={isbn}
            onChange={(e) => setIsbn(e.target.value)}
            required
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
            required
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
        {msg ? <p className="text-red-700">{msg}</p> : null}
        <button type="submit" className="rounded bg-zinc-900 px-3 py-1.5 text-white">
          Save
        </button>
      </form>
    </div>
  );
}
