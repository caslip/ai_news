import axios, { AxiosError } from "axios";
import { useAuthStore } from "@/stores/authStore";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface ApiErrorResponse {
  detail?: string;
  message?: string;
  error?: string;
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ============================================================
// Writer API Types
// ============================================================

export interface Draft {
  id: string;
  title: string;
  content: string;
  status: "generating" | "completed" | "failed";
  word_count: number;
  style: string;
  tone: string;
  length: string;
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

export interface BatchDeleteResponse {
  deleted_count: number;
}

/**
 * 获取草稿列表
 */
export const getDrafts = async (params?: {
  status?: string;
  page?: number;
  page_size?: number;
}): Promise<DraftListResponse> => {
  try {
    const response = await apiClient.get<DraftListResponse>("/api/writer/drafts/", { params });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "获取草稿列表失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};

/**
 * 获取单个草稿
 */
export const getDraft = async (draftId: string): Promise<Draft> => {
  try {
    const response = await apiClient.get<Draft>(`/api/writer/drafts/${draftId}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "获取草稿详情失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};

/**
 * 删除草稿
 */
export const deleteDraft = async (draftId: string): Promise<void> => {
  try {
    await apiClient.delete(`/api/writer/drafts/${draftId}`);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "删除草稿失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};

/**
 * 批量删除草稿
 */
export const batchDeleteDrafts = async (draftIds: string[]): Promise<BatchDeleteResponse> => {
  try {
    const response = await apiClient.post<BatchDeleteResponse>("/api/writer/drafts/batch-delete", {
      draft_ids: draftIds,
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "批量删除草稿失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};

/**
 * 获取模板列表
 */
export const getTemplates = async (): Promise<TemplateListResponse> => {
  try {
    const response = await apiClient.get<TemplateListResponse>("/api/writer/templates/");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "获取模板列表失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};

/**
 * 生成内容
 */
export const generateContent = async (data: GenerateRequest): Promise<GenerateResponse> => {
  try {
    const response = await apiClient.post<GenerateResponse>("/api/writer/generate", data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "生成内容失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};

/**
 * 获取写作统计
 */
export const getWriterStats = async (): Promise<WriterStats> => {
  try {
    const response = await apiClient.get<WriterStats>("/api/writer/drafts/stats");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "获取统计数据失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
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
      try {
        const { useAuthStore } = require("@/stores/authStore");
        useAuthStore.getState().logout();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      } catch {
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      }
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
