"use client";

import useSWR from "swr";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiGetBook, apiGetMember, apiMemberBorrowedBooks, ApiError } from "@/lib/api-client";

export default function MemberDetailPage() {
  const params = useParams();
  const id = String(params.id ?? "");
  const { data: member, error: e1 } = useSWR(id ? ["member", id] : null, () => apiGetMember(id));
  const { data: borrowed, error: e2 } = useSWR(id ? ["borrowed", id] : null, () =>
    apiMemberBorrowedBooks(id),
  );
  const bookIds = Array.from(new Set((borrowed ?? []).map((r) => r.book_id)));
  const { data: bookTitles } = useSWR(
    bookIds.length > 0 ? ["book-titles", ...bookIds] : null,
    async () => {
      const entries = await Promise.all(
        bookIds.map(async (bookId) => {
          try {
            const b = await apiGetBook(bookId);
            return [bookId, b.title] as const;
          } catch {
            return [bookId, bookId] as const;
          }
        }),
      );
      return Object.fromEntries(entries) as Record<string, string>;
    },
  );

  const error = e1 || e2;
  const errMsg =
    error instanceof ApiError
      ? error.body || error.message
      : error instanceof Error
        ? error.message
        : "";

  if (errMsg) return <p className="text-sm text-red-700">{errMsg}</p>;
  if (!member) return <p className="text-sm text-zinc-600">Loading…</p>;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-zinc-900">{member.name}</h1>
        <Link href={`/members/${id}/edit`} className="text-sm text-blue-700 underline">
          Edit
        </Link>
      </div>
      <dl className="mb-8 grid gap-2 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-zinc-500">Email</dt>
          <dd>{member.email}</dd>
        </div>
        <div>
          <dt className="text-zinc-500">Phone</dt>
          <dd>{member.phone}</dd>
        </div>
        {member.address ? (
          <div className="sm:col-span-2">
            <dt className="text-zinc-500">Address</dt>
            <dd>{member.address}</dd>
          </div>
        ) : null}
      </dl>

      <h2 className="mb-2 text-lg font-medium text-zinc-800">Books currently borrowed</h2>
      <div className="overflow-x-auto rounded border border-zinc-200 bg-white">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-zinc-200 bg-zinc-50">
            <tr>
              <th className="px-3 py-2">Loan ID</th>
              <th className="px-3 py-2">Book Name</th>
              <th className="px-3 py-2">Borrowed</th>
              <th className="px-3 py-2">Due</th>
              <th className="px-3 py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {(borrowed ?? []).length === 0 ? (
              <tr>
                <td colSpan={5} className="px-3 py-4 text-zinc-500">
                  No active loans.
                </td>
              </tr>
            ) : (
              (borrowed ?? []).map((r) => (
                <tr key={r.id} className="border-b border-zinc-100">
                  <td className="px-3 py-2 font-mono text-xs">{r.id}</td>
                  <td className="px-3 py-2">{bookTitles?.[r.book_id] ?? r.book_id}</td>
                  <td className="px-3 py-2">{r.borrowed_at}</td>
                  <td className="px-3 py-2">{r.due_date ?? "—"}</td>
                  <td className="px-3 py-2">{r.status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
