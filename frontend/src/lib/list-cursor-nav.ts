/**
 * WHY: Cursor-based list APIs only expose `next_page_token`; to offer "Previous" we must
 * remember which token produced the current page so we can walk back through the stack.
 */
export type CursorNav = {
  cursor: string;
  /** Tokens we already left behind when going forward — last entry is the page before `cursor`. */
  backStack: string[];
};

export function initialCursorNav(): CursorNav {
  return { cursor: "", backStack: [] };
}

export function goNextCursor(nav: CursorNav, nextToken: string): CursorNav {
  return {
    cursor: nextToken,
    backStack: [...nav.backStack, nav.cursor],
  };
}

export function goPrevCursor(nav: CursorNav): CursorNav | null {
  if (nav.backStack.length === 0) return null;
  const prev = nav.backStack[nav.backStack.length - 1];
  return {
    cursor: prev,
    backStack: nav.backStack.slice(0, -1),
  };
}
