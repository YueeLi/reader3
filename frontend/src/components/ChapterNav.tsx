import { Link } from "react-router-dom";

export default function ChapterNav({
  bookId,
  currentIndex,
  total
}: {
  bookId: string;
  currentIndex: number;
  total: number;
}) {
  const prevIndex = currentIndex > 0 ? currentIndex - 1 : null;
  const nextIndex = currentIndex < total - 1 ? currentIndex + 1 : null;

  return (
    <div className="chapter-nav">
      {prevIndex === null ? (
        <span className="ghost-button disabled">Previous</span>
      ) : (
        <Link className="ghost-button" to={`/read/${bookId}/${prevIndex}`}>
          Previous
        </Link>
      )}
      {nextIndex === null ? (
        <span className="ghost-button disabled">Next</span>
      ) : (
        <Link className="ghost-button" to={`/read/${bookId}/${nextIndex}`}>
          Next
        </Link>
      )}
    </div>
  );
}
