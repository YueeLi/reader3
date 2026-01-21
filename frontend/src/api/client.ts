export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8123";

export function resolveApiUrl(path: string): string {
  return new URL(path, API_BASE_URL).toString();
}

export function resolveAssetUrl(url?: string): string | undefined {
  if (!url) {
    return url;
  }
  if (
    url.startsWith("http://") ||
    url.startsWith("https://") ||
    url.startsWith("data:")
  ) {
    return url;
  }
  return resolveApiUrl(url);
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(resolveApiUrl(path));
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}
