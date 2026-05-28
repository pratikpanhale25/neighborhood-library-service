"use client";

import useSWR from "swr";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { apiGetMember, apiUpdateMember, ApiError } from "@/lib/api-client";
import { FormDialog } from "@/components/FormDialog";
import { normalizeOptionalTrimmed, requireTrimmedNonEmpty } from "@/lib/form-validation";
import { useAsyncAction } from "@/lib/use-async-action";

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
  const { pending, run } = useAsyncAction();

  useEffect(() => {
    if (!data) return;
    setName(data.name);
    setEmail(data.email);
    setPhone(data.phone);
    setAddress(data.address ?? "");
  }, [data]);

  function handleClose() {
    router.push("/members");
  }

  async function onSave(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");

    const n = requireTrimmedNonEmpty(name, "Name");
    const em = requireTrimmedNonEmpty(email, "Email");
    const ph = requireTrimmedNonEmpty(phone, "Phone");
    if (!n.ok) {
      setMsg(n.error);
      return;
    }
    if (!em.ok) {
      setMsg(em.error);
      return;
    }
    if (!ph.ok) {
      setMsg(ph.error);
      return;
    }

    await run(async () => {
      try {
        await apiUpdateMember(id, {
          name: n.value,
          email: em.value,
          phone: ph.value,
          address: normalizeOptionalTrimmed(address),
        });
        router.push("/members");
      } catch (ex) {
        setMsg(ex instanceof ApiError ? ex.body || ex.message : "Save failed");
      }
    });
  }

  if (isLoading) return <p className="text-sm text-zinc-600">Loading…</p>;
  if (error)
    return (
      <p className="text-sm text-red-700">
        {error instanceof ApiError ? error.body || error.message : "Error"}
      </p>
    );

  // WHY: Reuse FormDialog for edit so Create/Edit share the same modal shell and behavior as list create.
  return (
    <FormDialog
      open={Boolean(data)}
      title="Edit member"
      submitLabel="Save"
      pending={pending}
      onClose={handleClose}
      onSubmit={onSave}
    >
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block sm:col-span-2">
          <span className="text-zinc-600">Name</span>
          <input
            className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-zinc-600">Email</span>
          <input
            type="email"
            className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-zinc-600">Phone</span>
          <input
            className="mt-1 w-full rounded border border-zinc-300 px-2 py-1"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
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
      {msg ? <p className="text-sm text-red-700">{msg}</p> : null}
    </FormDialog>
  );
}
