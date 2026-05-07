import { redirect } from "next/navigation";

import { getSession } from "@/lib/session";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  if (await getSession()) {
    redirect("/dashboard");
  }
  redirect("/login");
}
