import { useRef, useState, type ChangeEvent, type DragEvent } from "react";
import { useNavigate } from "react-router-dom";
import { importEpub } from "../api/books";
import { LIBRARY_REFRESH_EVENT } from "../app/events";

const toolCards = [
  {
    title: "EPUB to PDF",
    description: "Generate a print-ready PDF with preserved typography.",
    action: "Queue PDF",
    status: "coming"
  },
  {
    title: "EPUB to Markdown",
    description: "Extract clean Markdown for notes, CMS, or doc pipelines.",
    action: "Queue Markdown",
    status: "coming"
  },
  {
    title: "Extract Illustrations",
    description: "Pull cover art, inline images, and chapter art assets.",
    action: "Collect Assets",
    status: "coming"
  },
  {
    title: "Metadata Snapshot",
    description: "Export title, author, and chapter list as structured JSON.",
    action: "Generate Snapshot",
    status: "coming"
  }
];

export default function ToolsPage() {
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
  const [isDragActive, setIsDragActive] = useState(false);
  const navigate = useNavigate();
  const duplicateMarker = "Book already imported";

  const handleImportClick = () => {
    if (importPhase !== "idle") {
      return;
    }
    fileInputRef.current?.click();
  };

  const handleImportFile = async (file: File) => {
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
      navigate("/libra");
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

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    event.target.value = "";
    await handleImportFile(file);
  };

  const handleOverlayDismiss = () => {
    setImportPhase("idle");
    setImportResult(null);
    setImportingFileName(null);
  };

  const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (!isDragActive) {
      setIsDragActive(true);
    }
  };

  const handleDragLeave = (event: DragEvent<HTMLDivElement>) => {
    if (event.currentTarget.contains(event.relatedTarget as Node)) {
      return;
    }
    setIsDragActive(false);
  };

  const handleDrop = async (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragActive(false);
    const file = event.dataTransfer.files?.[0];
    if (file) {
      await handleImportFile(file);
    }
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
    <section className="tools-page">
      <div className="tools-hero">
        <div className="tools-hero-copy">
          <p className="eyebrow">Tools</p>
          <h1>Everything you need to process new books.</h1>
          <p className="subhead">
            Import an EPUB once, then route it through conversion, illustration
            capture, and metadata workflows.
          </p>
          <div className="tools-hero-actions">
            <button
              className="accent-button"
              type="button"
              onClick={handleImportClick}
              disabled={importPhase !== "idle"}
            >
              {importPhase === "importing" ? "Processing..." : "Import EPUB"}
            </button>
            <span className="tools-hero-meta">EPUB only. Up to 500 MB.</span>
          </div>
        </div>
        <div className="tools-hero-status">
          <div className="status-card">
            <span className="status-label">Queue</span>
            <strong className="status-value">Ready</strong>
            <p>Processing happens locally with API support.</p>
          </div>
          <div className="status-card">
            <span className="status-label">Outputs</span>
            <strong className="status-value">4 pipelines</strong>
            <p>PDF, Markdown, Assets, Metadata.</p>
          </div>
        </div>
      </div>

      <div
        className={isDragActive ? "tools-dropzone dragging" : "tools-dropzone"}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        role="button"
        tabIndex={0}
        onClick={handleImportClick}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            handleImportClick();
          }
        }}
      >
        <div className="dropzone-content">
          <p className="dropzone-title">Drop your EPUB here</p>
          <p className="dropzone-subhead">
            We will catalog chapters, cover, and metadata automatically.
          </p>
        </div>
        <div className="dropzone-badges">
          <span>Cover Art</span>
          <span>Chapters</span>
          <span>Metadata</span>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".epub"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
      </div>

      <div className="tools-grid">
        {toolCards.map((tool) => (
          <article className="tool-card" key={tool.title}>
            <div>
              <h3>{tool.title}</h3>
              <p>{tool.description}</p>
            </div>
            <div className="tool-card-footer">
              <button
                className="ghost-button disabled"
                type="button"
                disabled
              >
                {tool.action}
              </button>
              <span className="tool-status">Coming soon</span>
            </div>
          </article>
        ))}
      </div>

      <div className="tools-pipeline">
        <div>
          <p className="eyebrow">Workflow</p>
          <h2>Suggested processing order</h2>
          <p className="subhead">
            Keep conversions consistent by following a predictable, repeatable
            pipeline.
          </p>
        </div>
        <div className="pipeline-steps">
          <div className="pipeline-step">
            <span className="step-index">01</span>
            <div>
              <h3>Import and validate</h3>
              <p>Check chapters, cover art, and metadata integrity.</p>
            </div>
          </div>
          <div className="pipeline-step">
            <span className="step-index">02</span>
            <div>
              <h3>Generate deliverables</h3>
              <p>Create PDFs and Markdown for review or publishing.</p>
            </div>
          </div>
          <div className="pipeline-step">
            <span className="step-index">03</span>
            <div>
              <h3>Collect assets</h3>
              <p>Export illustrations and metadata snapshots.</p>
            </div>
          </div>
        </div>
      </div>

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
              <p className="import-meta">{importMessage}</p>
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
    </section>
  );
}
