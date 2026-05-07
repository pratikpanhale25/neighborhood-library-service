/**
 * REST client for the FastAPI backend (`NEXT_PUBLIC_API_BASE_URL`, default http://127.0.0.1:8000).
 */

const defaultBase = "http://127.0.0.1:8000";

export function apiBaseUrl(): string {
  const v = process.env.NEXT_PUBLIC_API_BASE_URL;
  return (v && v.replace(/\/$/, "")) || defaultBase;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${apiBaseUrl()}${path.startsWith("/") ? path : `/${path}`}`;
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(init?.headers ?? {}),
  };
  const res = await fetch(url, { ...init, headers });
  const text = await res.text();
  if (!res.ok) {
    throw new ApiError(`HTTP ${res.status}`, res.status, text);
  }
  if (!text) return {} as T;
  return JSON.parse(text) as T;
}

export async function apiListBooks(params?: { page_size?: number; page_token?: string }) {
  const q = new URLSearchParams();
  if (params?.page_size) q.set("page_size", String(params.page_size));
  if (params?.page_token) q.set("page_token", params.page_token);
  const qs = q.toString();
  return apiJson<{
    items: Array<{
      id: string;
      title: string;
      author: string;
      isbn: string;
      publication_year: number | null;
      total_copies: number;
      available_copies: number;
      created_at: string;
      updated_at: string;
    }>;
    next_page_token: string;
  }>(`/books${qs ? `?${qs}` : ""}`);
}

export async function apiGetBook(id: string) {
  return apiJson<{
    id: string;
    title: string;
    author: string;
    isbn: string;
    publication_year: number | null;
    total_copies: number;
    available_copies: number;
    created_at: string;
    updated_at: string;
  }>(`/books/${encodeURIComponent(id)}`);
}

export async function apiCreateBook(body: {
  title: string;
  author: string;
  isbn: string;
  publication_year?: number | null;
  total_copies?: number;
}) {
  return apiJson<unknown>("/books", { method: "POST", body: JSON.stringify(body) });
}

export async function apiUpdateBook(
  id: string,
  body: {
    title: string;
    author: string;
    isbn: string;
    publication_year?: number | null;
    total_copies?: number | null;
  },
) {
  return apiJson<unknown>(`/books/${encodeURIComponent(id)}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export async function apiListMembers(params?: { page_size?: number; page_token?: string }) {
  const q = new URLSearchParams();
  if (params?.page_size) q.set("page_size", String(params.page_size));
  if (params?.page_token) q.set("page_token", params.page_token);
  const qs = q.toString();
  return apiJson<{
    items: Array<{
      id: string;
      name: string;
      email: string;
      phone: string;
      address: string | null;
      created_at: string;
      updated_at: string;
    }>;
    next_page_token: string;
  }>(`/members${qs ? `?${qs}` : ""}`);
}

export async function apiGetMember(id: string) {
  return apiJson<{
    id: string;
    name: string;
    email: string;
    phone: string;
    address: string | null;
    created_at: string;
    updated_at: string;
  }>(`/members/${encodeURIComponent(id)}`);
}

export async function apiCreateMember(body: {
  name: string;
  email: string;
  phone: string;
  address?: string | null;
}) {
  return apiJson<unknown>("/members", { method: "POST", body: JSON.stringify(body) });
}

export async function apiUpdateMember(
  id: string,
  body: { name: string; email: string; phone: string; address?: string | null },
) {
  return apiJson<unknown>(`/members/${encodeURIComponent(id)}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export async function apiMemberBorrowedBooks(memberId: string) {
  return apiJson<
    Array<{
      id: string;
      member_id: string;
      book_id: string;
      borrowed_at: string;
      due_date: string | null;
      returned_at: string | null;
      status: string;
    }>
  >(`/members/${encodeURIComponent(memberId)}/borrowed-books`);
}

export async function apiBorrow(body: {
  member_id: string;
  book_id: string;
  due_date?: string | null;
  loan_period_days?: number | null;
}) {
  return apiJson<unknown>("/borrow", { method: "POST", body: JSON.stringify(body) });
}

export async function apiReturn(body: {
  loan_id?: string | null;
  member_id?: string | null;
  book_id?: string | null;
}) {
  const payload: Record<string, string> = {};
  if (body.loan_id) payload.loan_id = body.loan_id;
  if (body.member_id) payload.member_id = body.member_id;
  if (body.book_id) payload.book_id = body.book_id;
  return apiJson<unknown>("/return", { method: "POST", body: JSON.stringify(payload) });
}

export async function apiBorrowRecords(params?: {
  member_id?: string;
  book_id?: string;
  status?: string;
  page_size?: number;
  page_token?: string;
}) {
  const q = new URLSearchParams();
  if (params?.member_id) q.set("member_id", params.member_id);
  if (params?.book_id) q.set("book_id", params.book_id);
  if (params?.status) q.set("status", params.status);
  if (params?.page_size) q.set("page_size", String(params.page_size));
  if (params?.page_token) q.set("page_token", params.page_token);
  const qs = q.toString();
  return apiJson<{
    items: Array<{
      id: string;
      member_id: string;
      book_id: string;
      borrowed_at: string;
      due_date: string | null;
      returned_at: string | null;
      status: string;
    }>;
    next_page_token: string;
  }>(`/borrow-records${qs ? `?${qs}` : ""}`);
}

export async function apiListFines(params?: {
  member_id?: string;
  status?: "pending" | "paid" | "waived" | "any";
  page_size?: number;
  page_token?: string;
}) {
  const q = new URLSearchParams();
  if (params?.member_id) q.set("member_id", params.member_id);
  if (params?.status) q.set("status", params.status);
  if (params?.page_size) q.set("page_size", String(params.page_size));
  if (params?.page_token) q.set("page_token", params.page_token);
  const qs = q.toString();
  return apiJson<{
    items: Array<{
      id: string;
      loan_id: string;
      member_id: string;
      amount_cents: number;
      currency: string;
      status: string;
      reason: string;
      created_at: string;
      resolved_at: string | null;
      notes: string | null;
    }>;
    next_page_token: string;
  }>(`/fines${qs ? `?${qs}` : ""}`);
}

export async function apiPayFine(fineId: string, notes?: string) {
  return apiJson<unknown>(`/fines/${encodeURIComponent(fineId)}/pay`, {
    method: "POST",
    body: JSON.stringify({ notes: notes ?? "" }),
  });
}

export async function apiWaiveFine(fineId: string, notes?: string) {
  return apiJson<unknown>(`/fines/${encodeURIComponent(fineId)}/waive`, {
    method: "POST",
    body: JSON.stringify({ notes: notes ?? "" }),
  });
}
