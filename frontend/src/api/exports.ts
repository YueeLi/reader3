import { API_BASE_URL } from "./client";

export type ExportFormat = "markdown" | "pdf";
export type MarkdownMode = "single" | "chapters";

function getFilenameFromHeader(contentDisposition: string | null): string | null {
  if (!contentDisposition) {
    return null;
  }

  const match = contentDisposition.match(/filename\*?=([^;]+)/i);
  if (!match) {
    return null;
  }

  const value = match[1].trim();
  if (value.startsWith("UTF-8''")) {
    return decodeURIComponent(value.replace("UTF-8''", "").replace(/"/g, ""));
  }

  return value.replace(/"/g, "");
}

export async function downloadExport(
  bookId: string,
  format: ExportFormat,
  mode: MarkdownMode = "single"
): Promise<void> {
  const url = new URL(`/export/${bookId}/${format}`, API_BASE_URL);
  if (format === "markdown") {
    url.searchParams.set("mode", mode);
  }

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Export failed: ${response.status}`);
  }

  const blob = await response.blob();
  const filename = getFilenameFromHeader(
    response.headers.get("content-disposition")
  );
  const fallbackExt = format === "pdf" ? "pdf" : "md";
  const resolvedName = filename || `${bookId}.${fallbackExt}`;

  const blobUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = blobUrl;
  link.download = resolvedName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(blobUrl);
}
