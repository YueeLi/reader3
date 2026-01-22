import type { CSSProperties } from "react";
import { Link } from "react-router-dom";
import type { BookListItem } from "../types/book";
import { downloadExport } from "../api/exports";

export default function BookCard({
  book,
  style,
}: {
  book: BookListItem;
  style?: CSSProperties;
}) {
  const coverStyle = book.coverUrl
    ? ({ "--cover-image": `url(${book.coverUrl})` } as CSSProperties)
    : ({ "--cover-image": "linear-gradient(135deg, #f5c08f, #d3764d)" } as CSSProperties);

  return (
    <article className="book-card" style={style}>
      <div className="book-cover" style={coverStyle}>
        <span className="book-cover-image" aria-hidden="true" />
        <div className="book-cover-overlay" />
        <span className="book-chapters">{book.chapters} chapters</span>
      </div>
      <div className="book-info">
        <h3 className="book-title">{book.title}</h3>
        <p className="book-author">{book.author}</p>
        <div className="book-actions">
          <Link className="book-action-button primary" to={`/read/${book.id}/0`}>
            <svg
              className="book-action-icon"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M5 12h10.5l-3.8-3.8L13 6l6 6-6 6-1.3-2.2 3.8-3.8H5z"
                fill="currentColor"
              />
            </svg>
            Open
          </Link>
          <button
            className="book-action-button secondary"
            type="button"
            onClick={() => {
              void downloadExport(book.id, "markdown", "single");
            }}
          >
            <svg
              className="book-action-icon"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M12 4a1 1 0 0 1 1 1v7.6l2.6-2.6 1.4 1.4L12 16.4 7 11.4l1.4-1.4 2.6 2.6V5a1 1 0 0 1 1-1z"
                fill="currentColor"
              />
              <path d="M5 18h14v2H5z" fill="currentColor" />
            </svg>
            Export
          </button>
        </div>
      </div>
    </article>
  );
}
