/**
 * sources.test.tsx - 信源页面组件测试
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

const mockSources = [
  {
    id: "source-1",
    name: "机器之心",
    type: "rss" as const,
    config: { feed_url: "https://example.com/rss" },
    is_active: true,
    created_at: "2024-01-01T00:00:00Z",
  },
  {
    id: "source-2",
    name: "GitHub Trending",
    type: "github" as const,
    config: { language: "python" },
    is_active: true,
    created_at: "2024-01-02T00:00:00Z",
  },
  {
    id: "source-3",
    name: "Twitter Feed",
    type: "twitter" as const,
    config: { account: "@test" },
    is_active: false,
    created_at: "2024-01-03T00:00:00Z",
  },
];

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

vi.mock("@/lib/api", () => ({
  getSources: vi.fn().mockResolvedValue({
    items: mockSources,
    total: 3,
    page: 1,
    page_size: 100,
  }),
  createSource: vi.fn(),
  toggleSource: vi.fn(),
  deleteSource: vi.fn(),
  testSource: vi.fn(),
  batchDeleteSources: vi.fn().mockResolvedValue({
    deleted_count: 2,
    not_found_ids: [],
    total_requested: 2,
  }),
  Source: {},
  SourceCreate: {},
  SourceListResponse: {},
}));

vi.mock("@/stores/authStore", () => ({
  useAuthStore: vi.fn(() => ({
    token: "mock-token",
    logout: vi.fn(),
  })),
}));

describe("Sources Page - Batch Delete", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render source list", async () => {
    const queryClient = createTestQueryClient();
    const { default: SourcesPage } = await import("@/app/(main)/sources/page");

    render(
      <QueryClientProvider client={queryClient}>
        <SourcesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("机器之心")).toBeInTheDocument();
      expect(screen.getByText("GitHub Trending")).toBeInTheDocument();
    });
  });

  it("should show batch delete toolbar when sources are selected", async () => {
    const queryClient = createTestQueryClient();
    const { default: SourcesPage } = await import("@/app/(main)/sources/page");

    render(
      <QueryClientProvider client={queryClient}>
        <SourcesPage />
      </QueryClientProvider>
    );

    await waitFor(() => screen.getByText("机器之心"));

    const checkboxes = screen.getAllByRole("checkbox");
    expect(checkboxes.length).toBeGreaterThan(0);

    fireEvent.click(checkboxes[1]);

    await waitFor(() => {
      expect(screen.getByText(/已选中/)).toBeInTheDocument();
    });
  });

  it("should hide batch toolbar after clearing selection", async () => {
    const queryClient = createTestQueryClient();
    const { default: SourcesPage } = await import("@/app/(main)/sources/page");

    render(
      <QueryClientProvider client={queryClient}>
        <SourcesPage />
      </QueryClientProvider>
    );

    await waitFor(() => screen.getByText("机器之心"));

    const checkboxes = screen.getAllByRole("checkbox");
    fireEvent.click(checkboxes[1]);

    await waitFor(() => screen.getByText(/已选中/));

    const closeButtons = screen.getAllByRole("button");
    const closeButton = closeButtons.find((btn) => {
      const label = btn.getAttribute("aria-label");
      return label?.includes("清除选择");
    });
    if (closeButton) {
      fireEvent.click(closeButton);
    }

    await waitFor(() => {
      expect(screen.queryByText(/已选中/)).not.toBeInTheDocument();
    });
  });
});
