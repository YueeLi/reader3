export default function ReaderToolbar({
  bookTitle,
  chapterTitle,
  onExportPdf,
  onExportMarkdown
}: {
  bookTitle: string;
  chapterTitle?: string;
  onExportPdf: () => void;
  onExportMarkdown: () => void;
}) {
  return (
    <div className="reader-toolbar">
      <div>
        <span className="eyebrow">{bookTitle}</span>
        <h1>{chapterTitle || "Untitled"}</h1>
      </div>
      <div className="reader-actions">
        <button className="ghost-button" type="button" onClick={onExportMarkdown}>
          Export MD
        </button>
        <button className="accent-button" type="button" onClick={onExportPdf}>
          Export PDF
        </button>
      </div>
    </div>
  );
}
