import { type ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";

export default function AppShell({ children }: { children: ReactNode }) {
  const { pathname } = useLocation();
  const isHome = pathname === "/";
  const isLibra = pathname.startsWith("/libra") || pathname.startsWith("/read");
  const isTools = pathname.startsWith("/tools");

  return (
    <div className="app-shell">
      <header className={`app-header${isHome ? " home" : ""}`}>
        <div className="header-left">
          <Link to="/" className="logo">
            Reader3
          </Link>
          <span className="logo-tag">Studio</span>
        </div>
        <nav className="app-nav">
          <Link
            to="/"
            className={isHome ? "nav-link active" : "nav-link"}
            aria-current={isHome ? "page" : undefined}
          >
            Home
          </Link>
          <Link
            to="/libra"
            className={isLibra ? "nav-link active" : "nav-link"}
            aria-current={isLibra ? "page" : undefined}
          >
            Libra
          </Link>
          <Link
            to="/tools"
            className={isTools ? "nav-link active" : "nav-link"}
            aria-current={isTools ? "page" : undefined}
          >
            Tools
          </Link>
        </nav>
        <div className="header-actions">
          <Link className="ghost-button" to="/tools">
            Start a workflow
          </Link>
          <Link className="accent-button" to="/libra">
            Open Libra
          </Link>
        </div>
      </header>
      <main className="app-main">{children}</main>
      <footer className="app-footer">
        <span>Local-first EPUB workspace.</span>
        <span className="divider" />
        <span>Libra library and tools pipeline.</span>
      </footer>
    </div>
  );
}
