"use client";

import useSWR from "swr";
import { useState } from "react";
import Link from "next/link";
import { apiCreateMember, apiListMembers, ApiError } from "@/lib/api-client";

const fetcher = () => apiListMembers({ page_size: 100 });

export default function MembersPage() {
  const { data, error, isLoading, mutate } = useSWR("members-list", fetcher);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
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
      await apiCreateMember({ name, email, phone, address: address || null });
      setName("");
      setEmail("");
      setPhone("");
      setAddress("");
      await mutate();
    } catch (ex) {
      setFormErr(ex instanceof Error ? ex.message : "Create failed");
    }
  }

  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold text-zinc-900">Members</h1>

      <form
        onSubmit={onCreate}
        className="mb-8 space-y-3 rounded border border-zinc-200 bg-zinc-50 p-4 text-sm"
      >
        <h2 className="font-medium text-zinc-800">Add member</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block sm:col-span-2">
            <span className="text-zinc-600">Name</span>
            <input
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </label>
          <label className="block">
            <span className="text-zinc-600">Email</span>
            <input
              type="email"
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <label className="block">
            <span className="text-zinc-600">Phone</span>
            <input
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
            />
          </label>
          <label className="block sm:col-span-2">
            <span className="text-zinc-600">Address</span>
            <input
              className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
            />
          </label>
        </div>
        {formErr ? <p className="text-sm text-red-700">{formErr}</p> : null}
        <button type="submit" className="rounded bg-zinc-900 px-3 py-1.5 text-white">
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
              <th className="px-3 py-2 font-medium">Name</th>
              <th className="px-3 py-2 font-medium">Email</th>
              <th className="px-3 py-2 font-medium">Phone</th>
              <th className="px-3 py-2 font-medium" />
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && !isLoading ? (
              <tr>
                <td className="px-3 py-4 text-zinc-500" colSpan={4}>
                  No members yet.
                </td>
              </tr>
            ) : (
              rows.map((m) => (
                <tr key={m.id} className="border-b border-zinc-100">
                  <td className="px-3 py-2">{m.name}</td>
                  <td className="px-3 py-2">{m.email}</td>
                  <td className="px-3 py-2">{m.phone}</td>
                  <td className="px-3 py-2">
                    <Link href={`/members/${m.id}`} className="text-blue-700 underline">
                      View
                    </Link>{" "}
                    <Link href={`/members/${m.id}/edit`} className="text-blue-700 underline">
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
