"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { createSessionToken, SESSION_COOKIE } from "@/lib/session";

export async function loginAction(formData: FormData) {
  // WHY: trim so accidental spaces in the browser field do not fail the demo check.
  const username = (formData.get("username") ?? "").toString().trim();
  const password = (formData.get("password") ?? "").toString().trim();

  if (!username || !password) {
    redirect("/login?error=credentials");
  }

  if (username !== "admin" || password !== "admin") {
    redirect("/login?error=credentials");
  }

  let token: string;
  try {
    token = await createSessionToken();
  } catch {
    redirect("/login?error=config");
  }

  const jar = await cookies();
  jar.set(SESSION_COOKIE, token, {
    httpOnly: true,
    path: "/",
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7,
  });
  redirect("/dashboard");
}
