import { describe, expect, it } from "vitest";

import {
  bookDetailPath,
  booksListPath,
  borrowPath,
  finePayPath,
  memberBorrowedBooksPath,
} from "./api-endpoints";

describe("api-endpoints", () => {
  it("builds stable collection paths", () => {
    expect(booksListPath()).toBe("/books");
    expect(borrowPath()).toBe("/borrow");
  });

  it("encodes ids in path segments", () => {
    expect(bookDetailPath("abc/def")).toBe(`/books/${encodeURIComponent("abc/def")}`);
    expect(memberBorrowedBooksPath("m1")).toBe("/members/m1/borrowed-books");
    expect(finePayPath("f#1")).toBe(`/fines/${encodeURIComponent("f#1")}/pay`);
  });
});
