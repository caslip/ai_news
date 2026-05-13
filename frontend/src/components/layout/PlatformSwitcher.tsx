"use client";

import { ArrowRightLeft, Newspaper, PenLine } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/authStore";

interface PlatformSwitcherProps {
  /** Current platform name shown in sidebar */
  currentPlatform: "writer" | "news";
  collapsed?: boolean;
}

const PLATFORMS = {
  writer: {
    label: "AI Writer",
    targetLabel: "AI News",
    targetUrl: process.env.NEXT_PUBLIC_NEWS_URL || "http://localhost:3001",
    targetIcon: Newspaper,
  },
  news: {
    label: "AI News",
    targetLabel: "AI Writer",
    targetUrl: process.env.NEXT_PUBLIC_WRITER_URL || "http://localhost:3002",
    targetIcon: PenLine,
  },
} as const;

function buildCrossPlatformUrl(baseUrl: string, token: string | null, user: { id: string; email: string; nickname: string; role: string; avatar_url?: string } | null): string {
  if (!token) return baseUrl;
  const params = new URLSearchParams({ token });
  if (user) {
    params.set("userId", user.id);
    params.set("email", user.email);
    params.set("nickname", user.nickname);
    params.set("role", user.role);
    if (user.avatar_url) params.set("avatar_url", user.avatar_url);
  }
  return `${baseUrl}?${params.toString()}`;
}

export function PlatformSwitcher({ currentPlatform, collapsed = false }: PlatformSwitcherProps) {
  const { token, user } = useAuthStore();
  const platform = PLATFORMS[currentPlatform];
  const TargetIcon = platform.targetIcon;
  const targetUrl = buildCrossPlatformUrl(platform.targetUrl, token, user);

  if (collapsed) {
    return (
      <a
        href={targetUrl}
        className="group relative flex items-center justify-center h-10 w-full"
        title={`跳转到 ${platform.targetLabel}`}
      >
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 rounded-lg text-muted-foreground group-hover:text-foreground group-hover:bg-accent transition-colors"
        >
          <TargetIcon className="h-4 w-4" />
        </Button>
        <span className="absolute left-full ml-2 px-2 py-1 rounded-md bg-popover border text-xs whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-md">
          {platform.targetLabel}
        </span>
      </a>
    );
  }

  return (
    <a
      href={targetUrl}
      className="flex items-center gap-2 px-3 py-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-colors text-sm group"
    >
      <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
        <TargetIcon className="h-4 w-4 text-primary" />
      </div>
      <div className="flex flex-col min-w-0">
        <span className="font-medium truncate">{platform.targetLabel}</span>
        <span className="text-xs text-muted-foreground flex items-center gap-1">
          <ArrowRightLeft className="h-2.5 w-2.5" />
          切换平台
        </span>
      </div>
    </a>
  );
}
