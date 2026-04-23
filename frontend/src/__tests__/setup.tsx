import { afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";

afterEach(() => {
  cleanup();
});

vi.mock("@/lib/api", () => ({
  getSources: vi.fn(),
  createSource: vi.fn(),
  toggleSource: vi.fn(),
  deleteSource: vi.fn(),
  testSource: vi.fn(),
  batchDeleteSources: vi.fn(),
  Source: {},
  SourceCreate: {},
  SourceListResponse: {},
}));

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
