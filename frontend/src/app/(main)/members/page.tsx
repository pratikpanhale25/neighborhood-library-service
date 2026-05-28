"use client";

import useSWR from "swr";
import Link from "next/link";
import { useState } from "react";
import { apiCreateMember, apiListMembers, ApiError } from "@/lib/api-client";
import { DataTable } from "@/components/DataTable";
import { FormDialog } from "@/components/FormDialog";
import { ListPaginationBar } from "@/components/ListPaginationBar";
import { goNextCursor, goPrevCursor, initialCursorNav, type CursorNav } from "@/lib/list-cursor-nav";
import { normalizeOptionalTrimmed, requireTrimmedNonEmpty } from "@/lib/form-validation";
import { useAsyncAction } from "@/lib/use-async-action";

const PAGE_SIZE = 25;

export default function MembersPage() {
  const [listNav, setListNav] = useState<CursorNav>(initialCursorNav);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [formErr, setFormErr] = useState("");
  const { pending, run } = useAsyncAction();

  const { data, error, isLoading, mutate } = useSWR(
    ["members-list", listNav.cursor, PAGE_SIZE],
    () => apiListMembers({ page_size: PAGE_SIZE, page_token: listNav.cursor }),
  );

  const rows = data?.items ?? [];
  const errMsg =
    error instanceof ApiError
      ? error.body || error.message
      : error instanceof Error
        ? error.message
        : "";

  function openCreate() {
    setFormErr("");
    setName("");
    setEmail("");
    setPhone("");
    setAddress("");
    setDialogOpen(true);
  }

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormErr("");

    // WHY: trim and reject empty strings before the API call (HTML `required` allows whitespace-only).
    const n = requireTrimmedNonEmpty(name, "Name");
    const em = requireTrimmedNonEmpty(email, "Email");
    const ph = requireTrimmedNonEmpty(phone, "Phone");
    if (!n.ok) {
      setFormErr(n.error);
      return;
    }
    if (!em.ok) {
      setFormErr(em.error);
      return;
    }
    if (!ph.ok) {
      setFormErr(ph.error);
      return;
    }

    await run(async () => {
      try {
        await apiCreateMember({
          name: n.value,
          email: em.value,
          phone: ph.value,
          address: normalizeOptionalTrimmed(address),
        });
        setDialogOpen(false);
        await mutate();
      } catch (ex) {
        setFormErr(ex instanceof Error ? ex.message : "Create failed");
      }
    });
  }

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-2xl font-semibold text-zinc-900">Members</h1>
        <button
          type="button"
          className="rounded bg-zinc-900 px-3 py-1.5 text-sm text-white hover:bg-zinc-800"
          onClick={openCreate}
        >
          Add member
        </button>
      </div>

      <FormDialog
        open={dialogOpen}
        title="Add member"
        submitLabel="Create"
        pending={pending}
        onClose={() => !pending && setDialogOpen(false)}
        onSubmit={onCreate}
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
        {formErr ? <p className="text-sm text-red-700">{formErr}</p> : null}
      </FormDialog>

      {errMsg ? (
        <p className="mb-2 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{errMsg}</p>
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
        rowKey={(m) => m.id}
        emptyMessage="No members on this page."
        isLoading={isLoading}
        rows={rows}
        columns={[
          { header: "Name", cell: (m) => m.name },
          { header: "Email", cell: (m) => m.email },
          { header: "Phone", cell: (m) => m.phone },
          {
            header: "",
            cell: (m) => (
              <>
                <Link href={`/members/${m.id}`} className="text-blue-700 underline">
                  View
                </Link>{" "}
                <Link href={`/members/${m.id}/edit`} className="text-blue-700 underline">
                  Edit
                </Link>
              </>
            ),
          },
        ]}
      />
    </div>
  );
}
