import { useEffect, useRef, useState, type ChangeEvent, type ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { importEpub } from "../api/books";
import { LIBRARY_REFRESH_EVENT, LIBRARY_RESET_EVENT } from "./events";

export default function AppShell({ children }: { children: ReactNode }) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [importingFileName, setImportingFileName] = useState<string | null>(
    null,
  );
  const [toast, setToast] = useState<{
    type: "error" | "success";
    title: string;
    message: string;
  } | null>(null);
  const toastTimerRef = useRef<number | null>(null);
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
    setImportingFileName(file.name);
    const startedAt = Date.now();
    const minOverlayMs = 3000;
    setIsImporting(true);
    try {
      const book = await importEpub(file);
      const elapsed = Date.now() - startedAt;
      const remaining = Math.max(0, minOverlayMs - elapsed);
      if (remaining > 0) {
        await new Promise((resolve) => window.setTimeout(resolve, remaining));
      }
      setIsImporting(false);
      setImportingFileName(null);
      setToast({
        type: "success",
        title: "Import complete",
        message: `"${book.title}" is ready in your library.`
      });
      if (toastTimerRef.current) {
        window.clearTimeout(toastTimerRef.current);
      }
      toastTimerRef.current = window.setTimeout(() => {
        setToast(null);
        toastTimerRef.current = null;
      }, 3600);
      window.dispatchEvent(new Event(LIBRARY_REFRESH_EVENT));
      navigate("/");
    } catch (error) {
      console.error(error);
      const message =
        error instanceof Error
          ? error.message
          : "Import failed. Please confirm the API is running.";
      const elapsed = Date.now() - startedAt;
      const remaining = Math.max(0, minOverlayMs - elapsed);
      if (remaining > 0) {
        await new Promise((resolve) => window.setTimeout(resolve, remaining));
      }
      setIsImporting(false);
      setImportingFileName(null);
      setToast({
        type: "error",
        title: "Import blocked",
        message
      });
      if (toastTimerRef.current) {
        window.clearTimeout(toastTimerRef.current);
      }
      toastTimerRef.current = window.setTimeout(() => {
        setToast(null);
        toastTimerRef.current = null;
      }, 4800);
    }
  };

  const handleNewSession = () => {
    window.dispatchEvent(new Event(LIBRARY_RESET_EVENT));
    navigate("/");
  };

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) {
        window.clearTimeout(toastTimerRef.current);
      }
    };
  }, []);

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
      {isImporting ? (
        <div className="import-overlay" role="status" aria-live="polite" aria-busy="true">
          <div className="import-dialog">
            <div className="import-graphic">
              <div className="import-book">
                <span className="import-cover" />
                <span className="import-page page-1" />
                <span className="import-page page-2" />
                <span className="import-page page-3" />
              </div>
              <div className="import-progress">
                <span />
                <span />
                <span />
              </div>
            </div>
            <div className="import-content">
              <p className="import-eyebrow">Importing EPUB</p>
              <h2>Cataloging your new read</h2>
              <p className="import-meta">
                {importingFileName || "This might take a moment while we index pages."}
              </p>
            </div>
          </div>
        </div>
      ) : null}
      {toast ? (
        <div
          className="toast-stack"
          aria-live={toast.type === "error" ? "assertive" : "polite"}
        >
          <div
            className={`toast toast-${toast.type}`}
            role={toast.type === "error" ? "alert" : "status"}
          >
            <span className="toast-dot" aria-hidden="true" />
            <div className="toast-body">
              <span className="toast-title">{toast.title}</span>
              <span className="toast-message">{toast.message}</span>
            </div>
            <button
              className="toast-close"
              type="button"
              onClick={() => setToast(null)}
              aria-label="Dismiss notification"
            >
              x
            </button>
          </div>
        </div>
      ) : null}
      <main className="app-main">{children}</main>
      <footer className="app-footer">
        <span>Local-first EPUB reader.</span>
        <span className="divider" />
        <span>Frontend scaffold for upcoming auth.</span>
      </footer>
    </div>
  );
}
