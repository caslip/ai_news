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
  type DraftListResponse,
  type Draft,
  type TemplateListResponse,
  type GenerateRequest,
  type GenerateResponse,
  type WriterStats,
} from "@/lib/api";

export function useWriterStats() {
  return useQuery<WriterStats>({
    queryKey: ["writer-stats"],
    queryFn: getWriterStats,
  });
}

export function useDrafts(params?: { status?: string; page?: number; page_size?: number }) {
  return useQuery<DraftListResponse>({
    queryKey: ["drafts", params],
    queryFn: () => getDrafts(params),
  });
}

export function useDraft(draftId: string) {
  return useQuery<Draft>({
    queryKey: ["draft", draftId],
    queryFn: () => getDraft(draftId),
    enabled: !!draftId,
  });
}

export function useDeleteDraft() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteDraft,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["drafts"] });
      void queryClient.invalidateQueries({ queryKey: ["writer-stats"] });
    },
  });
}

export function useBatchDeleteDrafts() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: batchDeleteDrafts,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["drafts"] });
      void queryClient.invalidateQueries({ queryKey: ["writer-stats"] });
    },
  });
}

export function useTemplates() {
  return useQuery<TemplateListResponse>({
    queryKey: ["templates"],
    queryFn: getTemplates,
  });
}

export function useGenerateContent() {
  const queryClient = useQueryClient();
  return useMutation<GenerateResponse, Error, GenerateRequest>({
    mutationFn: generateContent,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["drafts"] });
      void queryClient.invalidateQueries({ queryKey: ["writer-stats"] });
    },
  });
}
