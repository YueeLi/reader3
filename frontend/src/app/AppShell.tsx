import { Link } from "react-router-dom";

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <Link to="/" className="logo">
          Reader3
        </Link>
        <div className="header-actions">
          <button className="ghost-button" type="button">
            Import EPUB
          </button>
          <button className="accent-button" type="button">
            New Session
          </button>
        </div>
      </header>
      <main className="app-main">{children}</main>
      <footer className="app-footer">
        <span>Local-first EPUB reader.</span>
        <span className="divider" />
        <span>Frontend scaffold for upcoming auth.</span>
      </footer>
    </div>
  );
}
