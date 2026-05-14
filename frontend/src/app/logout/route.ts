import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { SESSION_COOKIE } from "@/lib/session";

export async function GET(request: Request) {
  const jar = await cookies();
  // Next 15 `cookies().delete` accepts a single cookie descriptor (name + path must match how it was set).
  jar.delete({ name: SESSION_COOKIE, path: "/" });
  const url = new URL(request.url);
  return NextResponse.redirect(new URL("/login", url.origin));
}
