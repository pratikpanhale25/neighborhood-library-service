import { apiListBooks, apiListMembers } from "@/lib/api-client";

type BookRow = Awaited<ReturnType<typeof apiListBooks>>["items"][number];
type MemberRow = Awaited<ReturnType<typeof apiListMembers>>["items"][number];

const MAX_PAGES = 50;

/**
 * WHY: Circulation borrow/return selects need a full id→label map; one 200-item page is not
 * enough for large libraries, so we page through safely until the API reports no next token.
 */
export async function fetchAllBooksForSelect(
  listBooks: typeof apiListBooks,
): Promise<BookRow[]> {
  const out: BookRow[] = [];
  let page_token = "";
  for (let i = 0; i < MAX_PAGES; i++) {
    const page = await listBooks({ page_size: 200, page_token });
    out.push(...page.items);
    if (!page.next_page_token) break;
    page_token = page.next_page_token;
  }
  return out;
}

export async function fetchAllMembersForSelect(
  listMembers: typeof apiListMembers,
): Promise<MemberRow[]> {
  const out: MemberRow[] = [];
  let page_token = "";
  for (let i = 0; i < MAX_PAGES; i++) {
    const page = await listMembers({ page_size: 200, page_token });
    out.push(...page.items);
    if (!page.next_page_token) break;
    page_token = page.next_page_token;
  }
  return out;
}
