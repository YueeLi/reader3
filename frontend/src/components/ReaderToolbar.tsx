export default function ReaderToolbar({
  bookTitle,
  chapterTitle
}: {
  bookTitle: string;
  chapterTitle?: string;
}) {
  return (
    <div className="reader-toolbar">
      <div>
        <span className="eyebrow">{bookTitle}</span>
        <h1>{chapterTitle || "Untitled"}</h1>
      </div>
      <div className="reader-actions">
        <button className="ghost-button" type="button">
          Copy chapter
        </button>
        <button className="accent-button" type="button">
          Export book
        </button>
      </div>
    </div>
  );
}
