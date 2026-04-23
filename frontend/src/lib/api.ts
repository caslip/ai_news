import axios from "axios";
import { useAuthStore } from "@/stores/authStore";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ============================================================
// 信源管理 API
// ============================================================

export interface Source {
  id: string;
  name: string;
  type: "rss" | "twitter" | "github" | "netter";
  config: Record<string, any>;
  is_active: boolean;
  last_fetched_at?: string;
  created_by?: string;
  created_at: string;
  updated_at?: string;
}

export interface SourceListResponse {
  items: Source[];
  total: number;
  page: number;
  page_size: number;
}

export interface SourceCreate {
  name: string;
  type: "rss" | "twitter" | "github" | "netter";
  config: Record<string, any>;
}

export interface SourceUpdate {
  name?: string;
  type?: "rss" | "twitter" | "github" | "netter";
  config?: Record<string, any>;
  is_active?: boolean;
}

export interface SourceTestResponse {
  success: boolean;
  message: string;
  article_count: number;
}

export interface SourceBatchDeleteRequest {
  source_ids: string[];
}

export interface SourceBatchDeleteResponse {
  deleted_count: number;
  not_found_ids: string[];
  total_requested: number;
}

/**
 * 获取信源列表
 */
export const getSources = async (params?: {
  type?: string;
  is_active?: boolean;
  page?: number;
  page_size?: number;
}): Promise<SourceListResponse> => {
  const response = await apiClient.get<SourceListResponse>("/api/sources/", { params });
  return response.data;
};

/**
 * 获取单个信源
 */
export const getSource = async (sourceId: string): Promise<Source> => {
  const response = await apiClient.get<Source>(`/api/sources/${sourceId}`);
  return response.data;
};

/**
 * 创建新信源
 */
export const createSource = async (data: SourceCreate): Promise<Source> => {
  const response = await apiClient.post<Source>("/api/sources/", data);
  return response.data;
};

/**
 * 更新信源
 */
export const updateSource = async (sourceId: string, data: SourceUpdate): Promise<Source> => {
  const response = await apiClient.put<Source>(`/api/sources/${sourceId}`, data);
  return response.data;
};

/**
 * 切换信源启用/禁用状态
 */
export const toggleSource = async (sourceId: string): Promise<Source> => {
  const response = await apiClient.patch<Source>(`/api/sources/${sourceId}/toggle`);
  return response.data;
};

/**
 * 删除信源
 */
export const deleteSource = async (sourceId: string): Promise<void> => {
  await apiClient.delete(`/api/sources/${sourceId}`);
};

/**
 * 测试信源连接
 */
export const testSource = async (sourceId: string): Promise<SourceTestResponse> => {
  const response = await apiClient.post<SourceTestResponse>(`/api/sources/${sourceId}/test`);
  return response.data;
};

/**
 * 批量删除信源
 */
export const batchDeleteSources = async (
  sourceIds: string[]
): Promise<SourceBatchDeleteResponse> => {
  const response = await apiClient.post<SourceBatchDeleteResponse>(
    "/api/sources/batch-delete",
    { source_ids: sourceIds }
  );
  return response.data;
};

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
    // 如果是 logout 请求本身失败，不触发 logout 循环
    if (error.config?.url?.includes("/auth/logout")) {
      return Promise.reject(error);
    }
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);

export default apiClient;
