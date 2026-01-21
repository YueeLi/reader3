import type { BookListItem } from "../types/book";
import BookCard from "./BookCard";

export default function BookGrid({ books }: { books: BookListItem[] }) {
  if (!books.length) {
    return (
      <div className="empty-state">
        <h3>No books yet</h3>
        <p>Drag an EPUB into the backend or wire up the ingest API.</p>
      </div>
    );
  }

  return (
    <div className="book-grid">
      {books.map((book) => (
        <BookCard key={book.id} book={book} />
      ))}
    </div>
  );
}
