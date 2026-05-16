"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  PenLine,
  FileText,
  LayoutTemplate,
  Settings,
  ChevronLeft,
  ChevronRight,
  Search,
  FileEdit,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { PlatformSwitcher } from "@/components/layout/PlatformSwitcher";

const navItems = [
  { href: "/", label: "首页", icon: Home },
  { href: "/generate", label: "文章生成", icon: PenLine },
  { href: "/editor", label: "文本编辑器", icon: FileEdit },
  { href: "/drafts", label: "草稿箱", icon: FileText },
  { href: "/templates", label: "模板库", icon: LayoutTemplate },
  { href: "/settings", label: "设置", icon: Settings },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  user?: {
    nickname: string;
    email: string;
    avatar_url?: string;
    role: string;
  } | null;
}

export function Sidebar({ collapsed, onToggle, user }: SidebarProps) {
  const pathname = usePathname();
  const { logout } = useAuth();

  const displayName = user?.nickname?.trim() || user?.email?.split("@")[0] || "用户";
  const initial = displayName.charAt(0).toUpperCase();
  const isAdmin = user?.role === "admin";

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen border-r bg-card transition-all duration-300 flex flex-col",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between border-b px-4">
        {!collapsed && (
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold">
              AI
            </div>
            <span className="font-semibold">AI Writer</span>
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className={cn(collapsed && "mx-auto")}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Search */}
      {!collapsed && (
        <div className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="搜索草稿..."
              className="pl-9 h-9"
            />
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link key={item.href} href={item.href}>
              <Button
                variant={isActive ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start gap-3 h-10",
                  collapsed && "justify-center px-0 w-10"
                )}
              >
                <item.icon className="h-4 w-4 shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Button>
            </Link>
          );
        })}
      </nav>

      {/* Platform Switcher */}
      {!collapsed && (
        <div className="px-2 pb-2">
          <PlatformSwitcher currentPlatform="writer" />
        </div>
      )}
      {collapsed && (
        <div className="px-2 pb-2">
          <PlatformSwitcher currentPlatform="writer" collapsed />
        </div>
      )}

      {/* User */}
      <div className="border-t p-4">
        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className={cn(
                  "w-full justify-start gap-3 h-auto py-2",
                  collapsed && "justify-center px-0 w-10"
                )}
              >
                <Avatar className="h-8 w-8">
                  <AvatarImage src={user.avatar_url} />
                  <AvatarFallback>{initial}</AvatarFallback>
                </Avatar>
                {!collapsed && (
                  <div className="flex-1 min-w-0 text-left">
                    <p className="text-sm font-medium truncate">{displayName}</p>
                    <p className="text-xs text-muted-foreground">
                      {isAdmin ? (
                        <Badge variant="destructive" className="text-xs">
                          管理员
                        </Badge>
                      ) : (
                        "用户"
                      )}
                    </p>
                  </div>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuItem asChild>
                <Link href="/settings">个人设置</Link>
              </DropdownMenuItem>
              {isAdmin && (
                <DropdownMenuItem asChild>
                  <Link href="/admin">后台管理</Link>
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-destructive focus:text-destructive"
                onSelect={() => {
                  void logout();
                }}
              >
                退出登录
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <div className={cn("space-y-2", collapsed && "space-y-2")}>
            <Link href="/auth/login" className="block">
              <Button
                variant={collapsed ? "outline" : "default"}
                className={cn("w-full", collapsed && "px-0")}
                size={collapsed ? "icon" : "default"}
              >
                {collapsed ? (
                  <Avatar className="h-4 w-4" />
                ) : (
                  "登录"
                )}
              </Button>
            </Link>
          </div>
        )}
      </div>
    </aside>
  );
}
