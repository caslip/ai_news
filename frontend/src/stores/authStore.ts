import { create } from "zustand";
import { persist } from "zustand/middleware";
import apiClient from "@/lib/api";

interface User {
  id: string;
  email: string;
  nickname: string;
  avatar_url?: string;
  role: "user" | "admin";
  push_config: Record<string, unknown>;
  oauth_provider?: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, nickname: string) => Promise<boolean>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<boolean>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await apiClient.post("/api/auth/login", {
            email,
            password,
          });
          const { access_token, user } = response.data;
          
          apiClient.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          });
          return true;
        } catch (error: any) {
          const message = error.response?.data?.detail || "Login failed";
          set({ error: message, isLoading: false });
          return false;
        }
      },

      register: async (email: string, password: string, nickname: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await apiClient.post("/api/auth/register", {
            email,
            password,
            nickname,
          });
          const { access_token, user } = response.data;
          
          apiClient.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          });
          return true;
        } catch (error: any) {
          const message = error.response?.data?.detail || "Registration failed";
          set({ error: message, isLoading: false });
          return false;
        }
      },

      logout: async () => {
        try {
          await apiClient.post("/api/auth/logout");
        } catch {
          // Ignore logout errors
        }
        delete apiClient.defaults.headers.common["Authorization"];
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      fetchCurrentUser: async () => {
        const { token } = get();
        if (!token) return false;

        apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;

        try {
          const response = await apiClient.get("/api/auth/me");
          set({
            user: response.data,
            isAuthenticated: true,
          });
          return true;
        } catch {
          delete apiClient.defaults.headers.common["Authorization"];
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });
          return false;
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: "ai-news-auth",
      // 同时持久化用户信息，避免刷新/水合后侧边栏短暂或长期显示「登录」
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        if (state?.token) {
          apiClient.defaults.headers.common["Authorization"] = `Bearer ${state.token}`;
          // 用服务端数据校正本地缓存（头像、角色等）
          void state.fetchCurrentUser();
        }
      },
    }
  )
);
