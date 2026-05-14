/**
 * Central REST path segments for the library API.
 *
 * WHY: Keeps every backend URL path in one module so a version prefix or rename
 * is updated once instead of hunting string literals across the app.
 */

const enc = encodeURIComponent;

export function booksListPath(): string {
  return "/books";
}

export function bookDetailPath(bookId: string): string {
  return `/books/${enc(bookId)}`;
}

export function membersListPath(): string {
  return "/members";
}

export function memberDetailPath(memberId: string): string {
  return `/members/${enc(memberId)}`;
}

export function memberBorrowedBooksPath(memberId: string): string {
  return `/members/${enc(memberId)}/borrowed-books`;
}

export function borrowPath(): string {
  return "/borrow";
}

export function returnPath(): string {
  return "/return";
}

export function borrowRecordsPath(): string {
  return "/borrow-records";
}

export function finesListPath(): string {
  return "/fines";
}

export function finePayPath(fineId: string): string {
  return `/fines/${enc(fineId)}/pay`;
}

export function fineWaivePath(fineId: string): string {
  return `/fines/${enc(fineId)}/waive`;
}
