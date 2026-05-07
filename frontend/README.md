# Neighborhood Library — Next.js UI

Staff UI for books, members, borrow/return, and member detail. The browser calls the **FastAPI REST** backend (`NEXT_PUBLIC_API_BASE_URL`, default `http://127.0.0.1:8000`) via [`src/lib/api-client.ts`](./src/lib/api-client.ts) and **SWR**.

## Local dev

```bash
npm install
cp .env.local.example .env.local   # AUTH_SECRET + NEXT_PUBLIC_API_BASE_URL
npm run dev
```

Login: **admin** / **admin** (demo).
