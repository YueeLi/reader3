import type { BookDetail, BookListItem, ChapterContent } from "../types/book";
import { apiGet } from "./client";
import { mockBookDetail, mockBooks, mockChapter } from "./mock";

const useMock = import.meta.env.VITE_USE_MOCK === "true";

export async function fetchBooks(): Promise<BookListItem[]> {
  if (useMock) {
    return mockBooks;
  }
  return apiGet<BookListItem[]>("/api/books");
}

export async function fetchBookDetail(bookId: string): Promise<BookDetail> {
  if (useMock) {
    return { ...mockBookDetail, id: bookId };
  }
  return apiGet<BookDetail>(`/api/books/${bookId}`);
}

export async function fetchChapter(
  bookId: string,
  chapterIndex: number
): Promise<ChapterContent> {
  if (useMock) {
    return { ...mockChapter, id: String(chapterIndex), order: chapterIndex };
  }
  return apiGet<ChapterContent>(`/api/books/${bookId}/chapters/${chapterIndex}`);
}
