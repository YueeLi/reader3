import type { TocEntry } from "../types/book";
import { Link } from "react-router-dom";
import { downloadExport } from "../api/exports";

export default function TocSidebar({
  title,
  author,
  toc,
  bookId,
  activeIndex
}: {
  title: string;
  author: string;
  toc: TocEntry[];
  bookId: string;
  activeIndex: number;
}) {
  return (
    <aside className="toc-sidebar">
      <div className="toc-header">
        <span className="eyebrow">Reading</span>
        <h2>{title}</h2>
        <p>{author}</p>
      </div>
      <nav className="toc-list">
        {toc.map((entry) => {
          const isActive = entry.chapterIndex === activeIndex;
          const disabled = entry.chapterIndex === null;
          const to = entry.chapterIndex === null ? "#" : `/read/${bookId}/${entry.chapterIndex}`;

          return (
            <Link
              key={`${entry.title}-${entry.chapterIndex}-${entry.anchor ?? "root"}`}
              to={to}
              className={isActive ? "toc-link active" : "toc-link"}
              aria-disabled={disabled}
              style={{ paddingLeft: `${entry.depth * 14}px` }}
              onClick={(event) => {
                if (disabled) {
                  event.preventDefault();
                }
              }}
            >
              {entry.title}
            </Link>
          );
        })}
      </nav>
      <div className="toc-footer">
        <button
          className="ghost-button"
          type="button"
          onClick={() => {
            void downloadExport(bookId, "pdf");
          }}
        >
          Export PDF
        </button>
      </div>
    </aside>
  );
}
