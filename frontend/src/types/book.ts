export type BookListItem = {
  id: string;
  title: string;
  author: string;
  chapters: number;
  coverUrl?: string;
};

export type ChapterContent = {
  id: string;
  title: string;
  order: number;
  html: string;
};

export type TocEntry = {
  title: string;
  chapterIndex: number | null;
  anchor?: string | null;
  depth: number;
};

export type BookDetail = {
  id: string;
  title: string;
  author: string;
  chapters: number;
  toc: TocEntry[];
  coverUrl?: string;
};
