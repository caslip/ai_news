import axios from "axios";
import { useAuthStore } from "@/stores/authStore";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ============================================================
// Writer API
// ============================================================

export interface Draft {
  id: string;
  title: string;
  content: string;
  status: "generating" | "completed" | "failed";
  word_count: number;
  style: string;
  tone: string;
  source_url?: string;
  source_content?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface DraftListResponse {
  items: Draft[];
  total: number;
  page: number;
  page_size: number;
}

export interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  style: string;
  tone: string;
  length: string;
  use_count: number;
  created_at: string;
}

export interface TemplateListResponse {
  items: Template[];
  total: number;
}

export interface GenerateRequest {
  source_url?: string;
  source_content?: string;
  topic?: string;
  style: string;
  tone: string;
  length: "short" | "medium" | "long";
}

export interface GenerateResponse {
  id: string;
  status: "generating" | "completed" | "failed";
  content?: string;
  title?: string;
  word_count?: number;
  error_message?: string;
}

export interface WriterStats {
  today_count: number;
  total_drafts: number;
  total_words: number;
  avg_duration_seconds: number;
}

/**
 * 获取草稿列表
 */
export const getDrafts = async (params?: {
  status?: string;
  page?: number;
  page_size?: number;
}): Promise<DraftListResponse> => {
  const response = await apiClient.get<DraftListResponse>("/api/writer/drafts/", { params });
  return response.data;
};

/**
 * 获取单个草稿
 */
export const getDraft = async (draftId: string): Promise<Draft> => {
  const response = await apiClient.get<Draft>(`/api/writer/drafts/${draftId}`);
  return response.data;
};

/**
 * 删除草稿
 */
export const deleteDraft = async (draftId: string): Promise<void> => {
  await apiClient.delete(`/api/writer/drafts/${draftId}`);
};

/**
 * 批量删除草稿
 */
export const batchDeleteDrafts = async (draftIds: string[]): Promise<{ deleted_count: number }> => {
  const response = await apiClient.post<{ deleted_count: number }>("/api/writer/drafts/batch-delete", {
    draft_ids: draftIds,
  });
  return response.data;
};

/**
 * 获取模板列表
 */
export const getTemplates = async (): Promise<TemplateListResponse> => {
  const response = await apiClient.get<TemplateListResponse>("/api/writer/templates/");
  return response.data;
};

/**
 * 生成内容
 */
export const generateContent = async (data: GenerateRequest): Promise<GenerateResponse> => {
  const response = await apiClient.post<GenerateResponse>("/api/writer/generate", data);
  return response.data;
};

/**
 * 获取写作统计
 */
export const getWriterStats = async (): Promise<WriterStats> => {
  const response = await apiClient.get<WriterStats>("/api/writer/stats");
  return response.data;
};

// ============================================================
// Auth Interceptors
// ============================================================

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.config?.url?.includes("/auth/logout")) {
      return Promise.reject(error);
    }
    if (error.response?.status === 401) {
      // TODO: 暂时禁用，登录失败时不要刷新页面，方便调试
      // useAuthStore.getState().logout();
    }
    console.error("[API Error]", error.config?.method?.toUpperCase(), error.config?.url, {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message,
    });
    return Promise.reject(error);
  }
);

export default apiClient;
