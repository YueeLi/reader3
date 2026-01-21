import type { BookDetail, BookListItem, ChapterContent } from "../types/book";

export const mockBooks: BookListItem[] = [
  {
    id: "sample_book",
    title: "Reading in the Margins",
    author: "A. Librarian",
    chapters: 12,
    coverUrl: "https://images.unsplash.com/photo-1455885666463-1e5ab9e4130a?auto=format&fit=crop&w=800&q=80"
  },
  {
    id: "notes_on_attention",
    title: "Notes on Attention",
    author: "C. Editor",
    chapters: 8,
    coverUrl: "https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=800&q=80"
  }
];

export const mockBookDetail: BookDetail = {
  id: "sample_book",
  title: "Reading in the Margins",
  author: "A. Librarian",
  chapters: 2,
  toc: [
    { title: "Opening the Cover", chapterIndex: 0, anchor: null, depth: 0 },
    { title: "Chapter One", chapterIndex: 1, anchor: null, depth: 0 }
  ]
};

export const mockChapter: ChapterContent = {
  id: "0",
  title: "Opening the Cover",
  order: 0,
  html: "<p>Start with a single paragraph to verify layout.</p>"
};
