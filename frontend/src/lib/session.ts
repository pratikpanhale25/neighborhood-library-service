import { cookies } from "next/headers";
import { SignJWT, jwtVerify } from "jose";

export const SESSION_COOKIE = "library_session";

export function getAuthSecretBytes(): Uint8Array {
  const s = process.env.AUTH_SECRET;
  if (!s) {
    throw new Error("AUTH_SECRET is not set");
  }
  return new TextEncoder().encode(s);
}

export async function createSessionToken(): Promise<string> {
  return await new SignJWT({ sub: "admin" })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("7d")
    .sign(getAuthSecretBytes());
}

export async function getSession(): Promise<boolean> {
  const jar = await cookies();
  const v = jar.get(SESSION_COOKIE)?.value;
  if (!v) {
    return false;
  }
  try {
    await jwtVerify(v, getAuthSecretBytes());
    return true;
  } catch {
    return false;
  }
}
