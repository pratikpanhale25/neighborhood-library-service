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
import { DataTable } from "@/components/DataTable";
import { ListPaginationBar } from "@/components/ListPaginationBar";
import { fetchAllBooksForSelect, fetchAllMembersForSelect } from "@/lib/fetch-all-pages";
import { goNextCursor, goPrevCursor, initialCursorNav, type CursorNav } from "@/lib/list-cursor-nav";
import { requireTrimmedNonEmpty } from "@/lib/form-validation";
import { useAsyncAction } from "@/lib/use-async-action";

const LOANS_PAGE_SIZE = 25;

export default function CirculationPage() {
  const [listNav, setListNav] = useState<CursorNav>(initialCursorNav);
  const { data, error, isLoading, mutate } = useSWR(
    ["borrow-active", listNav.cursor, LOANS_PAGE_SIZE],
    () => apiBorrowRecords({ status: "active", page_size: LOANS_PAGE_SIZE, page_token: listNav.cursor }),
  );
  const { data: membersList, error: membersError } = useSWR("circulation-members-all", () =>
    fetchAllMembersForSelect(apiListMembers),
  );
  const { data: booksList, error: booksError } = useSWR("circulation-books-all", () =>
    fetchAllBooksForSelect(apiListBooks),
  );

  const [memberId, setMemberId] = useState("");
  const [bookId, setBookId] = useState("");
  const [loanId, setLoanId] = useState("");
  const [retMember, setRetMember] = useState("");
  const [retBook, setRetBook] = useState("");
  const [msg, setMsg] = useState("");
  const borrowLock = useAsyncAction();
  const returnLock = useAsyncAction();

  const rows = data?.items ?? [];
  const members = membersList ?? [];
  const books = booksList ?? [];
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
    if (!memberId || !bookId) {
      setMsg("Select both a member and a book.");
      return;
    }
    await borrowLock.run(async () => {
      try {
        await apiBorrow({ member_id: memberId, book_id: bookId });
        setMemberId("");
        setBookId("");
        await mutate();
      } catch (ex) {
        setMsg(ex instanceof ApiError ? ex.body || ex.message : "Borrow failed");
      }
    });
  }

  async function onReturn(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");

    const lid = loanId.trim();
    if (lid) {
      await returnLock.run(async () => {
        try {
          await apiReturn({ loan_id: lid });
          setLoanId("");
          setRetMember("");
          setRetBook("");
          await mutate();
        } catch (ex) {
          setMsg(ex instanceof ApiError ? ex.body || ex.message : "Return failed");
        }
      });
      return;
    }

    const m = requireTrimmedNonEmpty(retMember, "Member");
    const b = requireTrimmedNonEmpty(retBook, "Book");
    if (!m.ok) {
      setMsg(m.error);
      return;
    }
    if (!b.ok) {
      setMsg(b.error);
      return;
    }

    await returnLock.run(async () => {
      try {
        await apiReturn({ member_id: m.value, book_id: b.value });
        setLoanId("");
        setRetMember("");
        setRetBook("");
        await mutate();
      } catch (ex) {
        setMsg(ex instanceof ApiError ? ex.body || ex.message : "Return failed");
      }
    });
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
          <button
            type="submit"
            className="rounded bg-zinc-900 px-3 py-1.5 text-white disabled:opacity-50"
            disabled={borrowLock.pending}
            aria-busy={borrowLock.pending}
          >
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
              {returnBookIdsForMember.map((bid) => (
                <option key={bid} value={bid}>
                  {bookNameById[bid] ?? bid} ({bid})
                </option>
              ))}
            </select>
          </label>
          <button
            type="submit"
            className="rounded bg-zinc-900 px-3 py-1.5 text-white disabled:opacity-50"
            disabled={returnLock.pending}
            aria-busy={returnLock.pending}
          >
            Return
          </button>
        </form>
      </div>

      <div>
        <h2 className="mb-2 text-lg font-medium text-zinc-800">Active loans</h2>
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
          rowKey={(r) => r.id}
          emptyMessage="No active loans on this page."
          isLoading={isLoading}
          rows={rows}
          columns={[
            { header: "Loan", cellClassName: "font-mono text-xs", cell: (r) => r.id },
            { header: "Member Name", cell: (r) => memberNameById[r.member_id] ?? "—" },
            { header: "Member ID", cellClassName: "font-mono text-xs", cell: (r) => r.member_id },
            { header: "Book Name", cell: (r) => bookNameById[r.book_id] ?? "—" },
            { header: "Book ID", cellClassName: "font-mono text-xs", cell: (r) => r.book_id },
            { header: "Due", cell: (r) => r.due_date ?? "—" },
            { header: "Status", cell: (r) => r.status },
          ]}
        />
      </div>
    </div>
  );
}
