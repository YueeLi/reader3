import { useEffect, useMemo, useState } from "react";
import { fetchBooks } from "../api/books";
import type { BookListItem } from "../types/book";
import BookGrid from "../components/BookGrid";

const filters = ["All", "Recently Added", "In Progress", "Finished"];

export default function LibraryPage() {
  const [books, setBooks] = useState<BookListItem[]>([]);
  const [activeFilter, setActiveFilter] = useState(filters[0]);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");

  useEffect(() => {
    let mounted = true;
    setStatus("loading");
    fetchBooks()
      .then((data) => {
        if (mounted) {
          setBooks(data);
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
  }, []);

  const filteredBooks = useMemo(() => {
    const q = query.trim().toLowerCase();
    return books.filter((book) => {
      const matchesQuery = q
        ? `${book.title} ${book.author}`.toLowerCase().includes(q)
        : true;
      const matchesFilter = activeFilter === "All" || activeFilter === "Recently Added";
      return matchesQuery && matchesFilter;
    });
  }, [books, query, activeFilter]);

  return (
    <section className="library-page">
      <div className="library-hero">
        <div>
          <p className="eyebrow">Your shelf</p>
          <h1>Browse, annotate, and export without leaving your library.</h1>
          <p className="subhead">
            A lightweight reading workspace that keeps your EPUB collection close and
            searchable.
          </p>
        </div>
        <div className="library-stats">
          <div>
            <span className="stat-label">Books</span>
            <strong>{books.length}</strong>
          </div>
          <div>
            <span className="stat-label">Exports</span>
            <strong>Ready</strong>
          </div>
          <div>
            <span className="stat-label">Sync</span>
            <strong>Local</strong>
          </div>
        </div>
      </div>

      <div className="library-controls">
        <div className="chips">
          {filters.map((filter) => (
            <button
              key={filter}
              type="button"
              className={filter === activeFilter ? "chip active" : "chip"}
              onClick={() => setActiveFilter(filter)}
            >
              {filter}
            </button>
          ))}
        </div>
        <div className="search">
          <input
            type="search"
            placeholder="Search by title or author"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>
      </div>

      {status === "error" ? (
        <div className="empty-state">
          <h3>Library unavailable</h3>
          <p>Hook up the API or toggle mock data in `VITE_USE_MOCK`.</p>
        </div>
      ) : (
        <BookGrid books={filteredBooks} />
      )}
    </section>
  );
}
