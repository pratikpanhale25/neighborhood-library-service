import Link from "next/link";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/books", label: "Books" },
  { href: "/members", label: "Members" },
  { href: "/circulation", label: "Borrow / Return" },
  { href: "/fines", label: "Fines" },
];

export function AppNav() {
  return (
    <header className="border-b border-zinc-200 bg-white">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-4 px-4 py-3">
        <Link href="/dashboard" className="font-semibold text-zinc-900">
          Neighborhood Library
        </Link>
        <nav className="flex flex-wrap gap-3 text-sm">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="text-zinc-600 underline-offset-4 hover:text-zinc-900 hover:underline"
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto">
          <Link
            href="/logout"
            className="text-sm text-zinc-600 underline-offset-4 hover:text-zinc-900 hover:underline"
          >
            Log out
          </Link>
        </div>
      </div>
    </header>
  );
}
