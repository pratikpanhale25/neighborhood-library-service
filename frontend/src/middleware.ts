import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { jwtVerify } from "jose";

const SESSION_COOKIE = "library_session";

export async function middleware(request: NextRequest) {
  const secret = process.env.AUTH_SECRET;
  if (!secret) {
    return NextResponse.redirect(new URL("/login?error=config", request.url));
  }
  const token = request.cookies.get(SESSION_COOKIE)?.value;
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  try {
    await jwtVerify(token, new TextEncoder().encode(secret));
    return NextResponse.next();
  } catch {
    return NextResponse.redirect(new URL("/login", request.url));
  }
}

export const config = {
  matcher: ["/dashboard", "/books", "/members", "/loans", "/fines"],
};
