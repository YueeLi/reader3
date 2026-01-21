import { useRef, useState, type ChangeEvent, type ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { importEpub } from "../api/books";
import { LIBRARY_REFRESH_EVENT, LIBRARY_RESET_EVENT } from "./events";

export default function AppShell({ children }: { children: ReactNode }) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const navigate = useNavigate();

  const handleImportClick = () => {
    if (isImporting) {
      return;
    }
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    event.target.value = "";
    setIsImporting(true);
    try {
      await importEpub(file);
      window.dispatchEvent(new Event(LIBRARY_REFRESH_EVENT));
      navigate("/");
    } catch (error) {
      console.error(error);
      const message =
        error instanceof Error
          ? error.message
          : "Import failed. Please confirm the API is running.";
      window.alert(message);
    } finally {
      setIsImporting(false);
    }
  };

  const handleNewSession = () => {
    window.dispatchEvent(new Event(LIBRARY_RESET_EVENT));
    navigate("/");
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link to="/" className="logo">
          Reader3
        </Link>
        <div className="header-actions">
          <button
            className="ghost-button"
            type="button"
            onClick={handleImportClick}
            disabled={isImporting}
          >
            {isImporting ? "Importing..." : "Import EPUB"}
          </button>
          <button
            className="accent-button"
            type="button"
            onClick={handleNewSession}
          >
            New Session
          </button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".epub"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
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
