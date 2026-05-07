"use client";

import useSWR from "swr";
import { apiBaseUrl, apiBorrowRecords, apiJson, apiListBooks, apiListMembers, ApiError } from "@/lib/api-client";

async function health() {
  return apiJson<{ status: string }>("/health");
}

export default function DashboardPage() {
  const { data: h, error: he } = useSWR("health", health);
  const { data: books } = useSWR("dash-books", () => apiListBooks({ page_size: 200 }));
  const { data: members } = useSWR("dash-members", () => apiListMembers({ page_size: 200 }));
  const { data: loans } = useSWR("dash-loans", () => apiBorrowRecords({ status: "active", page_size: 200 }));

  const apiErr =
    he instanceof ApiError
      ? he.body || he.message
      : he instanceof Error
        ? he.message
        : "";

  const bookCount = books?.items.length ?? 0;
  const memberCount = members?.items.length ?? 0;
  const activeLoans = loans?.items.length ?? 0;

  return (
    <div>
      <h1 className="mb-2 text-2xl font-semibold text-zinc-900">Dashboard</h1>
      <p className="mb-4 text-sm text-zinc-600">
        REST API base: <code className="rounded bg-zinc-100 px-1">{apiBaseUrl()}</code>
      </p>
      {apiErr ? (
        <div className="mb-6 rounded border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <strong className="font-medium">API unreachable.</strong> {apiErr}
        </div>
      ) : (
        <p className="mb-6 rounded border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-900">
          API health: <strong>{h?.status ?? "ok"}</strong>
        </p>
      )}
      <dl className="mb-8 grid gap-4 sm:grid-cols-3 text-sm">
        <div className="rounded border border-zinc-200 bg-white p-4">
          <dt className="text-zinc-500">Books</dt>
          <dd className="text-2xl font-semibold">{bookCount}</dd>
        </div>
        <div className="rounded border border-zinc-200 bg-white p-4">
          <dt className="text-zinc-500">Members</dt>
          <dd className="text-2xl font-semibold">{memberCount}</dd>
        </div>
        <div className="rounded border border-zinc-200 bg-white p-4">
          <dt className="text-zinc-500">Active loans</dt>
          <dd className="text-2xl font-semibold">{activeLoans}</dd>
        </div>
      </dl>
      <ul className="flex flex-col gap-2 text-zinc-800">
        <li>
          <a href="/books" className="text-blue-700 underline hover:text-blue-900">
            Books
          </a>
        </li>
        <li>
          <a href="/members" className="text-blue-700 underline hover:text-blue-900">
            Members
          </a>
        </li>
        <li>
          <a href="/circulation" className="text-blue-700 underline hover:text-blue-900">
            Borrow / Return
          </a>
        </li>
      </ul>
    </div>
  );
}
