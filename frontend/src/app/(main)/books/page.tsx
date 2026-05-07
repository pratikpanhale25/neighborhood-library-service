"use client";

import useSWR from "swr";
import { useState } from "react";
import Link from "next/link";
import { apiCreateBook, apiListBooks, ApiError } from "@/lib/api-client";

const listFetcher = () => apiListBooks({ page_size: 100 });

export default function BooksPage() {
  const { data, error, isLoading, mutate } = useSWR("books-list", listFetcher);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [isbn, setIsbn] = useState("");
  const [copies, setCopies] = useState("1");
  const [formErr, setFormErr] = useState("");

  const rows = data?.items ?? [];
  const errMsg =
    error instanceof ApiError
      ? error.body || error.message
      : error instanceof Error
        ? error.message
        : "";

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormErr("");
    try {
      await apiCreateBook({
        title,
        author,
        isbn,
        total_copies: Math.max(1, parseInt(copies, 10) || 1),
      });
      setTitle("");
      setAuthor("");
      setIsbn("");
      setCopies("1");
      await mutate();
    } catch (ex) {
      setFormErr(ex instanceof Error ? ex.message : "Create failed");
    }
  }

  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold text-zinc-900">Books</h1>

      <form
        onSubmit={onCreate}
        className="mb-8 space-y-3 rounded border border-zinc-200 bg-zinc-50 p-4 text-sm"
      >
        <h2 className="font-medium text-zinc-800">Add book</h2>
        <div className="grid gap-3 sm:grid-cols-2">
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
              value={copies}
              onChange={(e) => setCopies(e.target.value)}
            />
          </label>
        </div>
        {formErr ? <p className="text-sm text-red-700">{formErr}</p> : null}
        <button
          type="submit"
          className="rounded bg-zinc-900 px-3 py-1.5 text-white hover:bg-zinc-800"
        >
          Create
        </button>
      </form>

      {isLoading ? <p className="text-sm text-zinc-600">Loading…</p> : null}
      {errMsg ? (
        <p className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{errMsg}</p>
      ) : null}

      <div className="overflow-x-auto rounded border border-zinc-200 bg-white">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-zinc-200 bg-zinc-50 text-zinc-700">
            <tr>
              <th className="px-3 py-2 font-medium">Title</th>
              <th className="px-3 py-2 font-medium">Author</th>
              <th className="px-3 py-2 font-medium">Book Number</th>
              <th className="px-3 py-2 font-medium">Copies</th>
              <th className="px-3 py-2 font-medium">Available</th>
              <th className="px-3 py-2 font-medium" />
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && !isLoading ? (
              <tr>
                <td className="px-3 py-4 text-zinc-500" colSpan={6}>
                  No books yet.
                </td>
              </tr>
            ) : (
              rows.map((b) => (
                <tr key={b.id} className="border-b border-zinc-100">
                  <td className="px-3 py-2">{b.title}</td>
                  <td className="px-3 py-2">{b.author}</td>
                  <td className="px-3 py-2">{b.isbn}</td>
                  <td className="px-3 py-2">{b.total_copies}</td>
                  <td className="px-3 py-2">{b.available_copies}</td>
                  <td className="px-3 py-2">
                    <Link href={`/books/${b.id}/edit`} className="text-blue-700 underline">
                      Edit
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
