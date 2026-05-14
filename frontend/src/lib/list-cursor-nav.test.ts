import { describe, expect, it } from "vitest";

import { goNextCursor, goPrevCursor, initialCursorNav } from "./list-cursor-nav";

describe("list-cursor-nav", () => {
  it("walks forward then back across cursor tokens", () => {
    let nav = initialCursorNav();
    expect(nav.cursor).toBe("");
    expect(nav.backStack).toEqual([]);

    nav = goNextCursor(nav, "tok1");
    expect(nav.cursor).toBe("tok1");
    expect(nav.backStack).toEqual([""]);

    nav = goNextCursor(nav, "tok2");
    expect(nav.cursor).toBe("tok2");
    expect(nav.backStack).toEqual(["", "tok1"]);

    const p1 = goPrevCursor(nav);
    expect(p1).not.toBeNull();
    nav = p1!;
    expect(nav.cursor).toBe("tok1");
    expect(nav.backStack).toEqual([""]);

    const p0 = goPrevCursor(nav);
    expect(p0).not.toBeNull();
    nav = p0!;
    expect(nav.cursor).toBe("");
    expect(nav.backStack).toEqual([]);

    expect(goPrevCursor(nav)).toBeNull();
  });
});
