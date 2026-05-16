/**
 * Editor session storage utilities.
 * Uses sessionStorage with UUID keys to share content between tabs.
 * Each editor session gets a unique key; content is written before window.open().
 */

export interface EditorSession {
  key: string;
  title: string;
  content: string;
  sourceContent: string;
  topic: string;
  style: string;
  tone: string;
  length: string;
  createdAt: string;
}

const PREFIX = "ai-writer-editor:";
const LAST_KEY_STORAGE = "ai-writer:last-editor-key";

/**
 * Generate a new unique editor session key.
 */
export function generateEditorKey(): string {
  return `${PREFIX}${crypto.randomUUID()}`;
}

/**
 * Write an editor session to sessionStorage and track it as the last session.
 */
export function saveEditorSession(key: string, data: Omit<EditorSession, "key" | "createdAt">): void {
  try {
    const session: EditorSession = {
      key,
      createdAt: new Date().toISOString(),
      ...data,
    };
    sessionStorage.setItem(key, JSON.stringify(session));
    sessionStorage.setItem(LAST_KEY_STORAGE, key);
  } catch {
    // sessionStorage unavailable — ignore
  }
}

/**
 * Read an editor session from sessionStorage.
 */
export function loadEditorSession(key: string): EditorSession | null {
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) return null;
    return JSON.parse(raw) as EditorSession;
  } catch {
    return null;
  }
}

/**
 * Get the last opened editor session key.
 */
export function getLastEditorKey(): string | null {
  try {
    return sessionStorage.getItem(LAST_KEY_STORAGE);
  } catch {
    return null;
  }
}

/**
 * Remove an editor session from sessionStorage.
 */
export function removeEditorSession(key: string): void {
  try {
    sessionStorage.removeItem(key);
  } catch {
    // ignore
  }
}

/**
 * Convert markdown text to HTML for Tiptap using the marked library.
 * Handles all GFM features: tables, code blocks, strikethrough, task lists, etc.
 */
export async function markdownToHtml(text: string): Promise<string> {
  if (!text.trim()) return "";

  try {
    const { marked } = await import("marked");

    // Configure marked for GFM (tables, strikethrough, task lists)
    marked.use({
      gfm: true,
      breaks: true,
    });

    const html = await marked.parse(text);
    return String(html);
  } catch {
    // Fallback: return plain paragraphs if parsing fails
    return text
      .split("\n\n")
      .map((para) => `<p>${escapeHtml(para)}</p>`)
      .join("\n");
  }
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
