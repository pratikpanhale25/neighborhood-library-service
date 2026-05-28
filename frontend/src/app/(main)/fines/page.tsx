"use client";

import { useState } from "react";
import useSWR from "swr";

import { ApiError, apiListFines, apiListMembers, apiPayFine, apiWaiveFine } from "@/lib/api-client";
import { DataTable } from "@/components/DataTable";
import { ListPaginationBar } from "@/components/ListPaginationBar";
import { fetchAllMembersForSelect } from "@/lib/fetch-all-pages";
import { goNextCursor, goPrevCursor, initialCursorNav, type CursorNav } from "@/lib/list-cursor-nav";

const PAGE_SIZE = 25;

export default function FinesPage() {
  const [listNav, setListNav] = useState<CursorNav>(initialCursorNav);
  const { data, error, isLoading, mutate } = useSWR(
    ["fines-list", listNav.cursor, PAGE_SIZE],
    () => apiListFines({ status: "any", page_size: PAGE_SIZE, page_token: listNav.cursor }),
  );
  const { data: membersList, error: membersError } = useSWR("fines-member-directory", () =>
    fetchAllMembersForSelect(apiListMembers),
  );
  const [msg, setMsg] = useState("");
  const [pendingFineId, setPendingFineId] = useState<string | null>(null);

  const rows = data?.items ?? [];
  const members = membersList ?? [];
  const memberNameById = Object.fromEntries(members.map((m) => [m.id, m.name] as const));
  const allErrors = [error, membersError].filter(Boolean);
  const errMsg = allErrors
    .map((e) =>
      e instanceof ApiError ? e.body || e.message : e instanceof Error ? e.message : "",
    )
    .filter(Boolean)
    .join(" | ");

  async function onPay(fineId: string) {
    // WHY: allow only one fine mutation at a time so double-clicks cannot POST twice.
    if (pendingFineId) return;
    setMsg("");
    setPendingFineId(fineId);
    try {
      await apiPayFine(fineId);
      await mutate();
    } catch (ex) {
      setMsg(ex instanceof ApiError ? ex.body || ex.message : "Pay failed");
    } finally {
      setPendingFineId(null);
    }
  }

  async function onWaive(fineId: string) {
    // WHY: same serialization as Pay — shared pending state blocks overlapping actions.
    if (pendingFineId) return;
    setMsg("");
    setPendingFineId(fineId);
    try {
      await apiWaiveFine(fineId);
      await mutate();
    } catch (ex) {
      setMsg(ex instanceof ApiError ? ex.body || ex.message : "Waive failed");
    } finally {
      setPendingFineId(null);
    }
  }

  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold text-zinc-900">Fines</h1>
      {msg ? <p className="mb-3 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm">{msg}</p> : null}
      {errMsg ? (
        <p className="mb-3 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{errMsg}</p>
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
        rowKey={(f) => f.id}
        emptyMessage="No fines on this page."
        isLoading={isLoading}
        rows={rows}
        columns={[
          { header: "Fine ID", cellClassName: "font-mono text-xs", cell: (f) => f.id },
          { header: "Member Name", cell: (f) => memberNameById[f.member_id] ?? "—" },
          { header: "Member ID", cellClassName: "font-mono text-xs", cell: (f) => f.member_id },
          {
            header: "Amount",
            cell: (f) => (
              <>
                {(f.amount_cents / 100).toFixed(2)} {f.currency}
              </>
            ),
          },
          { header: "Status", cell: (f) => f.status },
          { header: "Reason", cell: (f) => f.reason },
          { header: "Created", cell: (f) => f.created_at },
          {
            header: "Actions",
            cell: (f) =>
              f.status === "pending" ? (
                <div className="flex gap-2">
                  <button
                    type="button"
                    className="rounded bg-emerald-600 px-2 py-1 text-xs text-white disabled:opacity-50"
                    onClick={() => onPay(f.id)}
                    disabled={pendingFineId !== null}
                    aria-busy={pendingFineId === f.id}
                  >
                    Pay
                  </button>
                  <button
                    type="button"
                    className="rounded bg-zinc-700 px-2 py-1 text-xs text-white disabled:opacity-50"
                    onClick={() => onWaive(f.id)}
                    disabled={pendingFineId !== null}
                    aria-busy={pendingFineId === f.id}
                  >
                    Waive
                  </button>
                </div>
              ) : (
                <span className="text-xs text-zinc-500">—</span>
              ),
          },
        ]}
      />
    </div>
  );
}
