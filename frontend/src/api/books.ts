import type { BookDetail, BookListItem, ChapterContent } from "../types/book";
import { apiGet, resolveAssetUrl, resolveApiUrl } from "./client";
import { mockBookDetail, mockBooks, mockChapter } from "./mock";

const useMock = import.meta.env.VITE_USE_MOCK === "true";
const booksBaseUrl = resolveApiUrl("/books/");

function resolveBookListItem(book: BookListItem): BookListItem {
  return {
    ...book,
    coverUrl: resolveAssetUrl(book.coverUrl)
  };
}

function resolveBookDetail(book: BookDetail): BookDetail {
  return {
    ...book,
    coverUrl: resolveAssetUrl(book.coverUrl)
  };
}

function resolveChapterHtml(html: string): string {
  if (!html) {
    return html;
  }
  return html
    .replaceAll('src="/books/', `src="${booksBaseUrl}`)
    .replaceAll("src='/books/", `src='${booksBaseUrl}`);
}

export async function fetchBooks(): Promise<BookListItem[]> {
  if (useMock) {
    return mockBooks.map((book) => resolveBookListItem(book));
  }
  const books = await apiGet<BookListItem[]>("/api/books");
  return books.map((book) => resolveBookListItem(book));
}

export async function fetchBookDetail(bookId: string): Promise<BookDetail> {
  if (useMock) {
    return resolveBookDetail({ ...mockBookDetail, id: bookId });
  }
  const book = await apiGet<BookDetail>(`/api/books/${bookId}`);
  return resolveBookDetail(book);
}

export async function fetchChapter(
  bookId: string,
  chapterIndex: number
): Promise<ChapterContent> {
  if (useMock) {
    return { ...mockChapter, id: String(chapterIndex), order: chapterIndex };
  }
  const chapter = await apiGet<ChapterContent>(
    `/api/books/${bookId}/chapters/${chapterIndex}`
  );
  return { ...chapter, html: resolveChapterHtml(chapter.html) };
}

export async function importEpub(file: File): Promise<BookListItem> {
  if (useMock) {
    throw new Error("Import is unavailable while VITE_USE_MOCK is true.");
  }
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(resolveApiUrl("/api/books/import"), {
    method: "POST",
    body: formData
  });
  if (!response.ok) {
    throw new Error(`Import failed: ${response.status}`);
  }
  const book = (await response.json()) as BookListItem;
  return resolveBookListItem(book);
}
