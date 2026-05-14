"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getDrafts,
  getDraft,
  deleteDraft,
  batchDeleteDrafts,
  getTemplates,
  generateContent,
  getWriterStats,
  ApiError,
  type DraftListResponse,
  type Draft,
  type TemplateListResponse,
  type GenerateRequest,
  type GenerateResponse,
  type WriterStats,
} from "@/lib/api";

export function useWriterStats() {
  return useQuery<WriterStats, ApiError>({
    queryKey: ["writer-stats"],
    queryFn: getWriterStats,
  });
}

export function useDrafts(params?: { status?: string; page?: number; page_size?: number }) {
  return useQuery<DraftListResponse, ApiError>({
    queryKey: ["drafts", params],
    queryFn: () => getDrafts(params),
  });
}

export function useDraft(draftId: string) {
  return useQuery<Draft, ApiError>({
    queryKey: ["draft", draftId],
    queryFn: () => getDraft(draftId),
    enabled: !!draftId,
  });
}

export function useDeleteDraft() {
  const queryClient = useQueryClient();
  return useMutation<void, ApiError, string>({
    mutationFn: deleteDraft,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["drafts"] });
      void queryClient.invalidateQueries({ queryKey: ["writer-stats"] });
    },
  });
}

export function useBatchDeleteDrafts() {
  const queryClient = useQueryClient();
  return useMutation<{ deleted_count: number }, ApiError, string[]>({
    mutationFn: batchDeleteDrafts,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["drafts"] });
      void queryClient.invalidateQueries({ queryKey: ["writer-stats"] });
    },
  });
}

export function useTemplates() {
  return useQuery<TemplateListResponse, ApiError>({
    queryKey: ["templates"],
    queryFn: getTemplates,
  });
}

export function useGenerateContent() {
  const queryClient = useQueryClient();
  return useMutation<GenerateResponse, ApiError, GenerateRequest>({
    mutationFn: generateContent,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["drafts"] });
      void queryClient.invalidateQueries({ queryKey: ["writer-stats"] });
    },
  });
}
