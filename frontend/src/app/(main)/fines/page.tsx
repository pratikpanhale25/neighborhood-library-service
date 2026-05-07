"use client";

import { useState } from "react";
import useSWR from "swr";

import { ApiError, apiListFines, apiListMembers, apiPayFine, apiWaiveFine } from "@/lib/api-client";

export const dynamic = "force-dynamic";

const finesFetcher = () => apiListFines({ status: "any", page_size: 200 });
const membersFetcher = () => apiListMembers({ page_size: 200 });

export default function FinesPage() {
  const { data, error, isLoading, mutate } = useSWR("fines-list", finesFetcher);
  const { data: membersData, error: membersError } = useSWR("members-list", membersFetcher);
  const [msg, setMsg] = useState("");

  const rows = data?.items ?? [];
  const members = membersData?.items ?? [];
  const memberNameById = Object.fromEntries(members.map((m) => [m.id, m.name] as const));
  const allErrors = [error, membersError].filter(Boolean);
  const errMsg = allErrors
    .map((e) =>
      e instanceof ApiError ? e.body || e.message : e instanceof Error ? e.message : "",
    )
    .filter(Boolean)
    .join(" | ");

  async function onPay(fineId: string) {
    setMsg("");
    try {
      await apiPayFine(fineId);
      await mutate();
    } catch (ex) {
      setMsg(ex instanceof ApiError ? ex.body || ex.message : "Pay failed");
    }
  }

  async function onWaive(fineId: string) {
    setMsg("");
    try {
      await apiWaiveFine(fineId);
      await mutate();
    } catch (ex) {
      setMsg(ex instanceof ApiError ? ex.body || ex.message : "Waive failed");
    }
  }

  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold text-zinc-900">Fines</h1>
      {msg ? <p className="mb-3 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm">{msg}</p> : null}
      {errMsg ? (
        <p className="mb-3 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{errMsg}</p>
      ) : null}
      {isLoading ? <p className="text-sm text-zinc-600">Loading…</p> : null}
      <div className="overflow-x-auto rounded border border-zinc-200 bg-white">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-zinc-200 bg-zinc-50">
            <tr>
              <th className="px-3 py-2">Fine ID</th>
              <th className="px-3 py-2">Member Name</th>
              <th className="px-3 py-2">Member ID</th>
              <th className="px-3 py-2">Amount</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Reason</th>
              <th className="px-3 py-2">Created</th>
              <th className="px-3 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && !isLoading ? (
              <tr>
                <td colSpan={8} className="px-3 py-4 text-zinc-500">
                  No fines yet.
                </td>
              </tr>
            ) : (
              rows.map((f) => (
                <tr key={f.id} className="border-b border-zinc-100">
                  <td className="px-3 py-2 font-mono text-xs">{f.id}</td>
                  <td className="px-3 py-2">{memberNameById[f.member_id] ?? "—"}</td>
                  <td className="px-3 py-2 font-mono text-xs">{f.member_id}</td>
                  <td className="px-3 py-2">
                    {(f.amount_cents / 100).toFixed(2)} {f.currency}
                  </td>
                  <td className="px-3 py-2">{f.status}</td>
                  <td className="px-3 py-2">{f.reason}</td>
                  <td className="px-3 py-2">{f.created_at}</td>
                  <td className="px-3 py-2">
                    {f.status === "pending" ? (
                      <div className="flex gap-2">
                        <button
                          type="button"
                          className="rounded bg-emerald-600 px-2 py-1 text-xs text-white"
                          onClick={() => onPay(f.id)}
                        >
                          Pay
                        </button>
                        <button
                          type="button"
                          className="rounded bg-zinc-700 px-2 py-1 text-xs text-white"
                          onClick={() => onWaive(f.id)}
                        >
                          Waive
                        </button>
                      </div>
                    ) : (
                      <span className="text-xs text-zinc-500">—</span>
                    )}
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
