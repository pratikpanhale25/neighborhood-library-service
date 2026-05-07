"use client";

import useSWR from "swr";
import { useState } from "react";
import {
  apiBorrow,
  apiBorrowRecords,
  apiListBooks,
  apiListMembers,
  apiReturn,
  ApiError,
} from "@/lib/api-client";

const activeFetcher = () => apiBorrowRecords({ status: "active", page_size: 100 });
const membersFetcher = () => apiListMembers({ page_size: 200 });
const booksFetcher = () => apiListBooks({ page_size: 200 });

export default function CirculationPage() {
  const { data, error, isLoading, mutate } = useSWR("borrow-active", activeFetcher);
  const { data: membersData, error: membersError } = useSWR("members-list", membersFetcher);
  const { data: booksData, error: booksError } = useSWR("books-list", booksFetcher);
  const [memberId, setMemberId] = useState("");
  const [bookId, setBookId] = useState("");
  const [loanId, setLoanId] = useState("");
  const [retMember, setRetMember] = useState("");
  const [retBook, setRetBook] = useState("");
  const [msg, setMsg] = useState("");

  const rows = data?.items ?? [];
  const members = membersData?.items ?? [];
  const books = booksData?.items ?? [];
  const memberNameById = Object.fromEntries(members.map((m) => [m.id, m.name] as const));
  const bookNameById = Object.fromEntries(books.map((b) => [b.id, b.title] as const));
  const activeBorrowerIds = Array.from(new Set(rows.map((r) => r.member_id)));
  const returnMemberOptions = activeBorrowerIds.map((id) => ({
    id,
    name: memberNameById[id] ?? id,
  }));
  const returnBookIdsForMember = retMember
    ? Array.from(new Set(rows.filter((r) => r.member_id === retMember).map((r) => r.book_id)))
    : [];

  const allErrors = [error, membersError, booksError].filter(Boolean);
  const errMsg = allErrors
    .map((e) =>
      e instanceof ApiError ? e.body || e.message : e instanceof Error ? e.message : "",
    )
    .filter(Boolean)
    .join(" | ");

  async function onBorrow(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");
    try {
      await apiBorrow({ member_id: memberId, book_id: bookId });
      setMemberId("");
      setBookId("");
      await mutate();
    } catch (ex) {
      setMsg(ex instanceof ApiError ? ex.body || ex.message : "Borrow failed");
    }
  }

  async function onReturn(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");
    try {
      if (loanId.trim()) {
        await apiReturn({ loan_id: loanId.trim() });
      } else {
        await apiReturn({ member_id: retMember.trim(), book_id: retBook.trim() });
      }
      setLoanId("");
      setRetMember("");
      setRetBook("");
      await mutate();
    } catch (ex) {
      setMsg(ex instanceof ApiError ? ex.body || ex.message : "Return failed");
    }
  }

  return (
    <div className="space-y-10">
      <h1 className="text-2xl font-semibold text-zinc-900">Borrow / Return</h1>
      {msg ? <p className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm">{msg}</p> : null}
      {errMsg ? <p className="text-sm text-red-700">{errMsg}</p> : null}

      <div className="grid gap-8 lg:grid-cols-2">
        <form onSubmit={onBorrow} className="space-y-3 rounded border border-zinc-200 p-4 text-sm">
          <h2 className="font-medium text-zinc-800">Borrow</h2>
          <label className="block">
            Member
            <select
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={memberId}
              onChange={(e) => setMemberId(e.target.value)}
              required
            >
              <option value="">Select Member</option>
              {members.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name} ({m.id})
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            Book
            <select
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={bookId}
              onChange={(e) => setBookId(e.target.value)}
              required
            >
              <option value="">Select Book</option>
              {books.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.title} ({b.id})
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className="rounded bg-zinc-900 px-3 py-1.5 text-white">
            Borrow
          </button>
        </form>

        <form onSubmit={onReturn} className="space-y-3 rounded border border-zinc-200 p-4 text-sm">
          <h2 className="font-medium text-zinc-800">Return</h2>
          <label className="block">
            Loan ID (optional if using member + book)
            <input
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1 font-mono text-xs"
              value={loanId}
              onChange={(e) => setLoanId(e.target.value)}
            />
          </label>
          <p className="text-xs text-zinc-500">Or member + book for the active loan:</p>
          <label className="block">
            Member
            <select
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={retMember}
              onChange={(e) => {
                setRetMember(e.target.value);
                setRetBook("");
              }}
            >
              <option value="">Select Member</option>
              {returnMemberOptions.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name} ({m.id})
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            Book
            <select
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={retBook}
              onChange={(e) => setRetBook(e.target.value)}
              disabled={!retMember}
            >
              <option value="">{retMember ? "Select Book" : "Select Member First"}</option>
              {returnBookIdsForMember.map((bookId) => (
                <option key={bookId} value={bookId}>
                  {bookNameById[bookId] ?? bookId} ({bookId})
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className="rounded bg-zinc-900 px-3 py-1.5 text-white">
            Return
          </button>
        </form>
      </div>

      <div>
        <h2 className="mb-2 text-lg font-medium text-zinc-800">Active loans</h2>
        {isLoading ? <p className="text-sm text-zinc-600">Loading…</p> : null}
        <div className="overflow-x-auto rounded border border-zinc-200 bg-white">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50">
              <tr>
                <th className="px-3 py-2">Loan</th>
                <th className="px-3 py-2">Member Name</th>
                <th className="px-3 py-2">Member ID</th>
                <th className="px-3 py-2">Book Name</th>
                <th className="px-3 py-2">Book ID</th>
                <th className="px-3 py-2">Due</th>
                <th className="px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-b border-zinc-100">
                  <td className="px-3 py-2 font-mono text-xs">{r.id}</td>
                  <td className="px-3 py-2">{memberNameById[r.member_id] ?? "—"}</td>
                  <td className="px-3 py-2 font-mono text-xs">{r.member_id}</td>
                  <td className="px-3 py-2">{bookNameById[r.book_id] ?? "—"}</td>
                  <td className="px-3 py-2 font-mono text-xs">{r.book_id}</td>
                  <td className="px-3 py-2">{r.due_date ?? "—"}</td>
                  <td className="px-3 py-2">{r.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
