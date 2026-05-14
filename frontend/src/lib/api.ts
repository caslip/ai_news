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
// 论文 API
// ============================================================

export interface Paper {
  id: string;
  source_id?: string;
  arxiv_id?: string;
  hf_paper_id?: string;
  title: string;
  url: string;
  summary?: string;
  author?: string;
  upvotes: number;
  thumbnail_url?: string;
  github_repo?: string;
  project_page?: string;
  hf_url?: string;
  primary_category?: string;
  categories: string[];
  tags: string[];
  published_at?: string;
  fetched_at: string;
  created_at: string;
}

export interface PaperListResponse {
  items: Paper[];
  total: number;
  page: number;
  page_size: number;
}

export interface PaperStats {
  today_count: number;
  week_count: number;
  month_count: number;
  total_count: number;
}

export const getPapers = async (params?: {
  source_type?: string;
  category?: string;
  min_upvotes?: number;
  time_range?: string;
  sort?: string;
  q?: string;
  page?: number;
  page_size?: number;
}): Promise<PaperListResponse> => {
  const cleanParams: Record<string, string | number> = {};
  if (params) {
    const num = (v: unknown) => {
      const n = typeof v === "number" ? v : parseInt(String(v), 10);
      return isNaN(n) ? undefined : n;
    };
    if (params.page !== undefined) { const v = num(params.page); if (v !== undefined) cleanParams.page = v; }
    if (params.page_size !== undefined) { const v = num(params.page_size); if (v !== undefined) cleanParams.page_size = v; }
    if (params.min_upvotes !== undefined) { const v = num(params.min_upvotes); if (v !== undefined) cleanParams.min_upvotes = v; }
    if (params.source_type) cleanParams.source_type = params.source_type;
    if (params.category) cleanParams.category = params.category;
    if (params.time_range) cleanParams.time_range = params.time_range;
    if (params.sort) cleanParams.sort = params.sort;
    if (params.q) cleanParams.q = params.q;
  }
  const response = await apiClient.get<PaperListResponse>("/api/papers/", { params: cleanParams });
  return response.data;
};

export const getPaperStats = async (): Promise<PaperStats> => {
  const response = await apiClient.get<PaperStats>("/api/papers/stats");
  return response.data;
};

// ============================================================
// 信源管理 API
// ============================================================

export interface Source {
  id: string;
  name: string;
  type: "rss" | "twitter" | "github" | "nitter" | "keyword" | "account" | "arxiv" | "hf_paper";
  config: Record<string, any>;
  is_active: boolean;
  last_fetched_at?: string;
  user_id?: string;
  monitor_type?: "keyword" | "account";
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

// 注意：信源管理页面只允许创建 rss 和 github 类型
// X 账号（nitter/twitter）和监控配置（keyword/account）通过 X 监控页面创建
export interface SourceCreate {
  name: string;
  type: "rss" | "github" | "arxiv" | "hf_paper";
  config: Record<string, any>;
  value?: string;
  params?: Record<string, unknown>;
  user_id?: string;
  monitor_type?: string;
}

export interface SourceUpdate {
  name?: string;
  type?: "rss" | "github";
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
    if (error.config?.url?.includes("/auth/logout")) {
      return Promise.reject(error);
    }
    if (error.response?.status === 401) {
      const { isAuthenticated, logout } = useAuthStore.getState();
      // TODO: 暂时禁用，登录失败时不要刷新页面，方便调试
      // if (isAuthenticated) {
      //   void logout();
      // }
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
