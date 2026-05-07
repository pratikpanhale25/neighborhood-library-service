import Link from "next/link";
import { redirect } from "next/navigation";

import { loginAction } from "@/app/login/actions";
import { getSession } from "@/lib/session";

export const dynamic = "force-dynamic";

type Props = {
  searchParams: Promise<{ error?: string }>;
};

export default async function LoginPage({ searchParams }: Props) {
  if (await getSession()) {
    redirect("/dashboard");
  }
  const params = await searchParams;
  const err = params.error;

  let message: string | null = null;
  if (err === "credentials") {
    message = "Invalid username or password.";
  } else if (err === "config") {
    message = "Server misconfiguration: set AUTH_SECRET in frontend/.env.local.";
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm rounded-lg border border-zinc-200 bg-white p-8 shadow-sm">
        <h1 className="mb-6 text-center text-xl font-semibold text-zinc-800">Library staff login</h1>
        {message ? (
          <p className="mb-4 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
            {message}
          </p>
        ) : null}
        <form action={loginAction} className="flex flex-col gap-4">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-zinc-600">Username</span>
            <input
              name="username"
              type="text"
              autoComplete="username"
              required
              className="rounded border border-zinc-300 px-3 py-2 text-zinc-900"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-zinc-600">Password</span>
            <input
              name="password"
              type="password"
              autoComplete="current-password"
              required
              className="rounded border border-zinc-300 px-3 py-2 text-zinc-900"
            />
          </label>
          <button
            type="submit"
            className="rounded bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800"
          >
            Sign in
          </button>
        </form>
        <p className="mt-6 text-center text-xs text-zinc-500">
          Demo credentials: <code className="rounded bg-zinc-100 px-1">admin</code> /{" "}
          <code className="rounded bg-zinc-100 px-1">admin</code>
        </p>
      </div>
      <p className="mt-8 text-xs text-zinc-400">
        <Link href="/" className="underline hover:text-zinc-600">
          Home
        </Link>
      </p>
    </main>
  );
}
