import { useRef, useState, type ChangeEvent, type DragEvent } from "react";
import { Link } from "react-router-dom";
import { fetchBookImages, importEpub } from "../api/books";
import { downloadExport } from "../api/exports";
import { LIBRARY_REFRESH_EVENT } from "../app/events";
import type { BookImageList, BookListItem } from "../types/book";

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
  const [currentBook, setCurrentBook] = useState<BookListItem | null>(null);
  const [imageList, setImageList] = useState<BookImageList | null>(null);
  const [imagePhase, setImagePhase] = useState<
    "idle" | "loading" | "ready" | "error"
  >("idle");
  const [imageError, setImageError] = useState<string | null>(null);
  const [showImages, setShowImages] = useState(false);
  const [exportPhase, setExportPhase] = useState<"idle" | "downloading">("idle");
  const [exportError, setExportError] = useState<string | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const duplicateMarker = "Book already imported";

  const resetPanels = () => {
    setCurrentBook(null);
    setImageList(null);
    setImagePhase("idle");
    setImageError(null);
    setShowImages(false);
    setExportPhase("idle");
    setExportError(null);
  };

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
    resetPanels();
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
        message: `"${book.title}" is ready for exports below.`
      });
      setCurrentBook(book);
      window.dispatchEvent(new Event(LIBRARY_REFRESH_EVENT));
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

  const handleDownloadPdf = async () => {
    if (!currentBook || exportPhase !== "idle") {
      return;
    }
    setExportPhase("downloading");
    setExportError(null);
    try {
      await downloadExport(currentBook.id, "pdf");
    } catch (error) {
      setExportError(
        error instanceof Error ? error.message : "PDF export failed."
      );
    } finally {
      setExportPhase("idle");
    }
  };

  const handleDownloadMarkdown = async (mode: "single" | "chapters") => {
    if (!currentBook || exportPhase !== "idle") {
      return;
    }
    setExportPhase("downloading");
    setExportError(null);
    try {
      await downloadExport(currentBook.id, "markdown", mode);
    } catch (error) {
      setExportError(
        error instanceof Error ? error.message : "Markdown export failed."
      );
    } finally {
      setExportPhase("idle");
    }
  };

  const loadImages = async () => {
    if (!currentBook || imagePhase === "loading") {
      return;
    }
    setImagePhase("loading");
    setImageError(null);
    try {
      const payload = await fetchBookImages(currentBook.id);
      setImageList(payload);
      setImagePhase("ready");
    } catch (error) {
      setImagePhase("error");
      setImageError(
        error instanceof Error ? error.message : "Failed to load images."
      );
    }
  };

  const handleImagesToggle = async () => {
    const next = !showImages;
    setShowImages(next);
    if (next && imagePhase !== "ready") {
      await loadImages();
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

  const imagesToShow =
    showImages && imageList ? imageList.images.slice(0, 8) : [];
  const showMoreTile =
    showImages && imageList ? imageList.images.length > 8 : false;
  const showEmptyTile =
    showImages && imageList ? imageList.images.length === 0 : false;
  const placeholderCount =
    showImages && imageList
      ? Math.max(
          0,
          9 - imagesToShow.length - (showMoreTile ? 1 : 0) - (showEmptyTile ? 1 : 0),
        )
      : 9;

  return (
    <section className="tools-page">
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
          <p className="dropzone-title">Import an EPUB</p>
          <p className="dropzone-subhead">
            Drop the file here or click to browse. We will index chapters and
            cover art automatically.
          </p>
          <button
            className="accent-button"
            type="button"
            onClick={(event) => {
              event.stopPropagation();
              handleImportClick();
            }}
            disabled={importPhase !== "idle"}
          >
            {importPhase === "importing" ? "Processing..." : "Choose file"}
          </button>
          <span className="dropzone-meta">EPUB only. Up to 500 MB.</span>
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

      <div className="tools-workspace">
        <article className="workbook-card">
          <div className="workbook-header">
            <div>
              <p className="eyebrow">Current EPUB</p>
              <h2>{currentBook ? currentBook.title : "No import yet"}</h2>
            </div>
            <span className="workbook-status">
              {currentBook ? "Ready" : "Idle"}
            </span>
          </div>
          <div className="workbook-body">
            {currentBook?.coverUrl ? (
              <img
                className="workbook-cover"
                src={currentBook.coverUrl}
                alt={`${currentBook.title} cover`}
              />
            ) : (
              <div className="workbook-cover placeholder" aria-hidden="true" />
            )}
          <div className="workbook-meta">
              <div>
                <span className="meta-label">Title</span>
                <p>{currentBook?.title || "Import an EPUB to begin."}</p>
              </div>
              <div>
                <span className="meta-label">Author</span>
                <p>{currentBook?.author || "—"}</p>
              </div>
              <div>
                <span className="meta-label">Chapters</span>
                <p>{currentBook ? currentBook.chapters : "—"}</p>
              </div>
            </div>
          </div>
          <div className="workbook-actions">
            {currentBook ? (
              <Link
                className="accent-button"
                to={`/read/${currentBook.id}/0`}
              >
                Preview
              </Link>
            ) : (
              <span className="accent-button disabled" aria-disabled="true">
                Preview
              </span>
            )}
            <button
              className="ghost-button"
              type="button"
              onClick={handleDownloadPdf}
              disabled={!currentBook || exportPhase === "downloading"}
            >
              PDF
            </button>
            <button
              className="ghost-button"
              type="button"
              onClick={() => handleDownloadMarkdown("single")}
              disabled={!currentBook || exportPhase === "downloading"}
            >
              Markdown
            </button>
            <button
              className="ghost-button"
              type="button"
              onClick={() => handleDownloadMarkdown("chapters")}
              disabled={!currentBook || exportPhase === "downloading"}
            >
              Zip
            </button>
          </div>
          {exportError ? (
            <p className="workbook-error">{exportError}</p>
          ) : null}
        </article>

        <div className="workbook-side">
          <article className="tool-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Illustrations</p>
                <h3>Visual assets</h3>
              </div>
              <button
                type="button"
                className="ghost-button"
                disabled={!currentBook}
                onClick={handleImagesToggle}
              >
                {showImages ? "Hide" : "View"} images
              </button>
            </div>
            <p className="panel-subhead">
              Browse extracted images stored with the EPUB.
            </p>
            {imagePhase === "loading" ? (
              <p className="panel-meta">Loading images…</p>
            ) : null}
            {imageError ? <p className="panel-error">{imageError}</p> : null}
            <div className="image-grid">
              {showImages && imageList ? (
                <>
                  {showEmptyTile ? (
                    <div className="image-tile more">No images</div>
                  ) : null}
                  {imagesToShow.map((image) => (
                    <div className="image-tile" key={image.url}>
                      <img src={image.url} alt={image.name} />
                    </div>
                  ))}
                  {showMoreTile ? (
                    <div className="image-tile more">More</div>
                  ) : null}
                  {Array.from({ length: placeholderCount }).map((_, index) => (
                    <div
                      className="image-tile placeholder"
                      key={`placeholder-${index}`}
                    />
                  ))}
                </>
              ) : (
                Array.from({ length: placeholderCount }).map((_, index) => (
                  <div className="image-tile placeholder" key={index} />
                ))
              )}
            </div>
          </article>
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
                    ? "Ready to process"
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
