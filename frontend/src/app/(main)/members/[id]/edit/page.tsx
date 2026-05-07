"use client";

import useSWR from "swr";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { apiGetMember, apiUpdateMember, ApiError } from "@/lib/api-client";

export default function EditMemberPage() {
  const params = useParams();
  const id = String(params.id ?? "");
  const router = useRouter();
  const { data, error, isLoading } = useSWR(id ? ["member", id] : null, () => apiGetMember(id));
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (!data) return;
    setName(data.name);
    setEmail(data.email);
    setPhone(data.phone);
    setAddress(data.address ?? "");
  }, [data]);

  async function onSave(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");
    try {
      await apiUpdateMember(id, {
        name,
        email,
        phone,
        address: address || null,
      });
      router.push("/members");
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
      <h1 className="mb-4 text-2xl font-semibold text-zinc-900">Edit member</h1>
      <form onSubmit={onSave} className="max-w-lg space-y-3 text-sm">
        <label className="block">
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
        <label className="block">
          <span className="text-zinc-600">Address</span>
          <input
            className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
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
