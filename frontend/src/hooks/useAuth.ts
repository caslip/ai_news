"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";

export function useAuth() {
  const router = useRouter();
  const { 
    user, 
    token, 
    isAuthenticated, 
    isLoading, 
    error,
    login, 
    register,
    logout: storeLogout, 
    fetchCurrentUser,
    clearError 
  } = useAuthStore();

  const handleLogin = useCallback(
    async (email: string, password: string): Promise<boolean> => {
      const success = await login(email, password);
      if (success) {
        router.push("/");
      }
      return success;
    },
    [login, router]
  );

  const handleRegister = useCallback(
    async (email: string, password: string, nickname: string): Promise<boolean> => {
      const success = await register(email, password, nickname);
      if (success) {
        router.push("/");
      }
      return success;
    },
    [register, router]
  );

  const handleLogout = useCallback(async (): Promise<void> => {
    await storeLogout();
    router.push("/auth/login");
  }, [storeLogout, router]);

  const handleFetchCurrentUser = useCallback(async (): Promise<boolean> => {
    return await fetchCurrentUser();
  }, [fetchCurrentUser]);

  const initiateGitHubOAuth = useCallback((): void => {
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/auth/oauth/github`;
  }, []);

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    fetchCurrentUser: handleFetchCurrentUser,
    initiateGitHubOAuth,
    clearError,
  };
}
