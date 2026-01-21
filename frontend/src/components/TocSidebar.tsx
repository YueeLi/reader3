import type { TocEntry } from "../types/book";

export default function TocSidebar({
  title,
  author,
  toc
}: {
  title: string;
  author: string;
  toc: TocEntry[];
}) {
  return (
    <aside className="toc-sidebar">
      <div className="toc-header">
        <span className="eyebrow">Reading</span>
        <h2>{title}</h2>
        <p>{author}</p>
      </div>
      <nav className="toc-list">
        {toc.map((entry) => (
          <a
            key={`${entry.title}-${entry.href}`}
            href={entry.href}
            style={{ paddingLeft: `${entry.depth * 14}px` }}
          >
            {entry.title}
          </a>
        ))}
      </nav>
      <div className="toc-footer">
        <button className="ghost-button" type="button">
          Export chapter
        </button>
      </div>
    </aside>
  );
}
