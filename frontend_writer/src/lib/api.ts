import axios, { AxiosError } from "axios";
import { useAuthStore } from "@/stores/authStore";
import { useRouter } from "next/navigation";

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
    const response = await apiClient.get<WriterStats>("/api/writer/stats");
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
// Chat API Types
// ============================================================

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  created_at?: string;
}

export interface ChatSession {
  session_id: string;
  title: string;
  message_count: number;
  created_at: string;
}

export interface ChatRequest {
  session_id?: string;
  message: string;
  model?: string;
  context_type?: "article" | "twitter" | "xiaohongshu" | null;
  source_content?: string | null;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  error?: string;
}

export interface ChatStreamEvent {
  event: "message" | "done" | "error";
  data: string;
}

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
      const router = useRouter;
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

// ============================================================
// Chat API Functions
// ============================================================

export interface ChatStreamOptions {
  sessionId: string;
  message: string;
  model?: string;
  context_type?: "article" | "twitter" | "xiaohongshu" | null;
  source_content?: string | null;
  onChunk: (content: string) => void;
  onDone: (sessionId: string) => void;
  onError: (error: string) => void;
}

/**
 * Create a new chat session
 */
export const createChatSession = async (): Promise<{ session_id: string }> => {
  try {
    const response = await apiClient.post<{ session_id: string }>("/api/writer/chat/sessions");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "创建聊天会话失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};

/**
 * Delete a chat session
 */
export const deleteChatSession = async (sessionId: string): Promise<void> => {
  try {
    await apiClient.delete(`/api/writer/chat/sessions/${sessionId}`);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "删除聊天会话失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};

/**
 * Get chat history for a session
 */
export const getChatHistory = async (sessionId: string): Promise<{ messages: ChatMessage[] }> => {
  try {
    const response = await apiClient.get<{ messages: ChatMessage[] }>(`/api/writer/chat/history/${sessionId}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "获取聊天历史失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};

/**
 * List all chat sessions
 */
export const listChatSessions = async (): Promise<{ sessions: ChatSession[] }> => {
  try {
    const response = await apiClient.get<{ sessions: ChatSession[] }>("/api/writer/chat/sessions");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "获取聊天会话列表失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};

/**
 * Non-streaming chat
 */
export const chatNonStream = async (data: ChatRequest): Promise<ChatResponse> => {
  try {
    const response = await apiClient.post<ChatResponse>("/api/writer/chat", data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "发送消息失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};

/**
 * Streaming chat using SSE
 */
export const chatStream = async (options: ChatStreamOptions): Promise<void> => {
  const { sessionId, message, model, context_type, source_content, onChunk, onDone, onError } = options;

  try {
    const response = await fetch(`${API_BASE_URL}/api/writer/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${useAuthStore.getState().token}`,
      },
      body: JSON.stringify({ session_id: sessionId, message, model, context_type, source_content }),
    });

    if (!response.ok) {
      onError(`HTTP ${response.status}`);
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      onError("No response body");
      return;
    }

    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data:")) {
            const data = line.slice(5).trim();
            if (!data) continue;

            try {
              const parsed = JSON.parse(data);
              if (parsed.content !== undefined) {
                onChunk(parsed.content);
              } else if (parsed.session_id !== undefined && parsed.done) {
                onDone(parsed.session_id);
              } else if (parsed.error) {
                onError(parsed.error);
              }
            } catch {
              // ignore parse errors for partial data
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  } catch (error) {
    onError(error instanceof Error ? error.message : "Network error");
  }
};

/**
 * Generate article from chat context
 */
export const chatToGenerate = async (data: ChatRequest): Promise<{ id: string }> => {
  try {
    const response = await apiClient.post<{ id: string }>("/api/writer/chat/generate", data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || "生成文章失败";
      throw new ApiError(message, axiosError.response?.status || 500, axiosError.response?.data);
    }
    throw error;
  }
};
