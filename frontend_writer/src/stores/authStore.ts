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
        } catch (error: any) {
          // 网络错误（CORS / 连接失败）时保留 token，等待后端恢复
          // 不要清除 token 和 isAuthenticated 状态
          if (error.response) {
            // 有 HTTP 响应但非 2xx，说明 token 真的无效，才清状态
            delete apiClient.defaults.headers.common["Authorization"];
            set({
              user: null,
              token: null,
              isAuthenticated: false,
            });
          }
          // status === undefined / Network Error：后端不可达，保留所有状态
          return false;
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: "ai-writer-auth",
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // 检查 pending_sso_v2（跨平台 SSO 跳转时 Zustand persist 还没写入）
        try {
          const pendingRaw = localStorage.getItem("pending_sso_v2");
          if (pendingRaw) {
            const pending = JSON.parse(pendingRaw);
            if (pending.token && pending.user) {
              localStorage.removeItem("pending_sso_v2");
              apiClient.defaults.headers.common["Authorization"] = `Bearer ${pending.token}`;
              state?.set({
                token: pending.token,
                user: pending.user,
                isAuthenticated: true,
              });
              return;
            }
          }
        } catch {
          // ignore
        }

        if (state?.token) {
          apiClient.defaults.headers.common["Authorization"] = `Bearer ${state.token}`;
          void state.fetchCurrentUser();
        } else {
          const cookies = document.cookie.split("; ");
          const ssoEntry = cookies.find((c) => c.startsWith("ai_sso_token="));
          if (ssoEntry) {
            const cookieToken = ssoEntry.split("=")[1];
            if (cookieToken) {
              apiClient.defaults.headers.common["Authorization"] = `Bearer ${cookieToken}`;
              apiClient.get("/api/auth/me").then((res) => {
                state?.set({
                  token: cookieToken,
                  user: res.data,
                  isAuthenticated: true,
                });
              }).catch(() => {
                document.cookie = "ai_sso_token=; Max-Age=0; path=/; SameSite=Lax";
              });
            }
          }
        }
      },
    }
  )
);
