import { Link } from "react-router-dom";
import type { BookListItem } from "../types/book";
import { downloadExport } from "../api/exports";

export default function BookCard({ book }: { book: BookListItem }) {
  const coverStyle = book.coverUrl
    ? { backgroundImage: `url(${book.coverUrl})` }
    : { backgroundImage: "linear-gradient(135deg, #f5c08f, #d3764d)" };

  return (
    <article className="book-card">
      <div className="book-cover" style={coverStyle}>
        <div className="book-cover-overlay" />
        <span className="book-chapters">{book.chapters} chapters</span>
      </div>
      <div className="book-info">
        <h3>{book.title}</h3>
        <p>{book.author}</p>
        <div className="book-actions">
          <Link className="ghost-button" to={`/read/${book.id}/0`}>
            Open
          </Link>
          <button
            className="ghost-button"
            type="button"
            onClick={() => {
              void downloadExport(book.id, "markdown", "single");
            }}
          >
            Export MD
          </button>
        </div>
      </div>
    </article>
  );
}
