import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchBookDetail, fetchChapter } from "../api/books";
import type { BookDetail, ChapterContent } from "../types/book";
import TocSidebar from "../components/TocSidebar";
import ReaderToolbar from "../components/ReaderToolbar";
import ChapterNav from "../components/ChapterNav";

export default function ReaderPage() {
  const { bookId = "", chapterIndex = "0" } = useParams();
  const [book, setBook] = useState<BookDetail | null>(null);
  const [chapter, setChapter] = useState<ChapterContent | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");

  useEffect(() => {
    let mounted = true;
    setStatus("loading");
    fetchBookDetail(bookId)
      .then((data) => {
        if (mounted) {
          setBook(data);
        }
        return fetchChapter(bookId, Number.parseInt(chapterIndex, 10));
      })
      .then((data) => {
        if (mounted) {
          setChapter(data);
          setStatus("idle");
        }
      })
      .catch(() => {
        if (mounted) {
          setStatus("error");
        }
      });

    return () => {
      mounted = false;
    };
  }, [bookId, chapterIndex]);

  const activeIndex = Number.parseInt(chapterIndex, 10);
  const chapterTitle = useMemo(() => chapter?.title, [chapter]);

  if (status === "error" || !book) {
    return (
      <section className="reader-shell empty">
        <div className="empty-state">
          <h3>Reader not ready</h3>
          <p>Connect the API endpoint to fetch chapters for this book.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="reader-shell">
      <TocSidebar title={book.title} author={book.author} toc={book.toc} />
      <div className="reader-main">
        <ReaderToolbar bookTitle={book.title} chapterTitle={chapterTitle} />
        <article className="reader-content">
          <h2>{chapterTitle}</h2>
          <div
            className="reader-html"
            dangerouslySetInnerHTML={{ __html: chapter?.html || "" }}
          />
        </article>
        <ChapterNav
          bookId={book.id}
          currentIndex={activeIndex}
          total={book.chapters}
        />
      </div>
    </section>
  );
}
