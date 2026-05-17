"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/authStore";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const { user, fetchCurrentUser } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    const { token } = useAuthStore.getState();
    if (token && !user) {
      void fetchCurrentUser().finally(() => setIsReady(true));
    } else {
      setIsReady(true);
    }
  }, []);

  useEffect(() => {
    if (isReady && !user) {
      router.push("/auth/login");
    }
  }, [isReady, user, router]);

  if (!isReady) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground text-sm">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        user={user}
      />
      <main
        className={cn(
          "min-h-screen transition-all duration-300",
          sidebarCollapsed ? "ml-16" : "ml-64"
        )}
      >
        {children}
      </main>
    </div>
  );
}
