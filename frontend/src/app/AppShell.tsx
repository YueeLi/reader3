import { useRef, useState, type ChangeEvent, type ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { importEpub } from "../api/books";
import { LIBRARY_REFRESH_EVENT, LIBRARY_RESET_EVENT } from "./events";

export default function AppShell({ children }: { children: ReactNode }) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [importingFileName, setImportingFileName] = useState<string | null>(
    null,
  );
  const [importPhase, setImportPhase] = useState<
    "idle" | "importing" | "success" | "error"
  >("idle");
  const [importResult, setImportResult] = useState<{
    title: string;
    message: string;
    type: "success" | "error";
  } | null>(null);
  const { pathname } = useLocation();
  const showLibraryActions = pathname === "/";
  const navigate = useNavigate();
  const duplicateMarker = "Book already imported";

  const handleImportClick = () => {
    if (importPhase !== "idle") {
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
    setImportPhase("importing");
    setImportResult(null);
    try {
      const book = await importEpub(file);
      const elapsed = Date.now() - startedAt;
      const remaining = Math.max(0, minOverlayMs - elapsed);
      if (remaining > 0) {
        await new Promise((resolve) => window.setTimeout(resolve, remaining));
      }
      setImportPhase("success");
      setImportResult({
        type: "success",
        title: "Import complete",
        message: `"${book.title}" is ready in your library.`
      });
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
      setImportPhase("error");
      setImportResult({
        type: "error",
        title: "Import failed",
        message
      });
    }
  };

  const handleNewSession = () => {
    window.dispatchEvent(new Event(LIBRARY_RESET_EVENT));
    navigate("/");
  };

  const handleOverlayDismiss = () => {
    setImportPhase("idle");
    setImportResult(null);
    setImportingFileName(null);
  };

  const importMessage = (() => {
    if (importPhase === "importing") {
      return (
        importingFileName ||
        "This might take a moment while we index pages."
      );
    }

    const message = importResult?.message || "Please try again.";
    const markerIndex = message.indexOf(duplicateMarker);
    if (markerIndex !== -1) {
      const detail = message
        .slice(markerIndex + duplicateMarker.length)
        .replace(/^:\s*/, "")
        .trim();
      return (
        <span className="import-reason">
          <span className="import-reason-tag">{duplicateMarker}</span>
          {detail ? <span className="import-reason-text">{detail}</span> : null}
        </span>
      );
    }

    return message;
  })();

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link to="/" className="logo">
          Reader3
        </Link>
        {showLibraryActions ? (
          <>
            <div className="header-actions">
              <button
                className="ghost-button"
                type="button"
                onClick={handleImportClick}
                disabled={importPhase !== "idle"}
              >
                {importPhase === "importing" ? "Importing..." : "Import EPUB"}
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
          </>
        ) : null}
      </header>
      {importPhase !== "idle" ? (
        <div
          className={`import-overlay ${importPhase}`}
          role={importPhase === "error" ? "alert" : "status"}
          aria-live={importPhase === "error" ? "assertive" : "polite"}
          aria-busy={importPhase === "importing"}
        >
          <div className={`import-dialog ${importPhase}`}>
            {importPhase === "importing" ? (
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
            ) : (
              <div className="import-result-graphic">
                <span className="import-result-icon" aria-hidden="true" />
                <span className="import-result-label">
                  {importPhase === "success" ? "Success" : "Failed"}
                </span>
              </div>
            )}
            <div className="import-content">
              <p className="import-eyebrow">
                {importPhase === "importing"
                  ? "Importing EPUB"
                  : importResult?.title || "Importing EPUB"}
              </p>
              <h2>
                {importPhase === "importing"
                  ? "Cataloging your new read"
                  : importPhase === "success"
                    ? "Ready on your shelf"
                    : "We couldn't add this book"}
              </h2>
              <p className="import-meta">
                {importMessage}
              </p>
              {importPhase !== "importing" ? (
                <div className="import-actions">
                  <button
                    type="button"
                    className="accent-button"
                    onClick={handleOverlayDismiss}
                  >
                    {importPhase === "success" ? "Done" : "Close"}
                  </button>
                </div>
              ) : null}
            </div>
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
