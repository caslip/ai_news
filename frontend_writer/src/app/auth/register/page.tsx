"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, User as LucideUser, Mail, ArrowLeft } from "lucide-react";
import apiClient from "@/lib/api";
import { useAuthStore, type User } from "@/stores/authStore";

const NEWS_REGISTER_URL = process.env.NEXT_PUBLIC_NEWS_URL || "http://localhost:3001";
const WRITER_URL = process.env.NEXT_PUBLIC_WRITER_URL || "http://localhost:3002";

function parseUserFromParams(): Record<string, string> {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("userId") || params.get("id") || "";
  return {
    id,
    email: params.get("email") || "",
    nickname: params.get("nickname") || "",
    avatar_url: params.get("avatar_url") || "",
    role: params.get("role") || "user",
  };
}

function syncToStore(token: string, userData: Record<string, unknown>) {
  apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  useAuthStore.setState({
    token,
    user: userData as unknown as User,
    isAuthenticated: true,
    isLoading: false,
    error: null,
  });
}

function redirectToNews() {
  const returnTo = `${WRITER_URL}/auth/register`;
  window.location.href = `${NEWS_REGISTER_URL}/auth/register?returnTo=${encodeURIComponent(returnTo)}`;
}

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const [localError, setLocalError] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (token) {
      syncToStore(token, parseUserFromParams());
      window.history.replaceState({}, "", window.location.pathname);
      window.location.href = "/";
      return;
    }

    const cookies = document.cookie.split("; ");
    const ssoEntry = cookies.find((c) => c.startsWith("ai_sso_token="));
    if (ssoEntry) {
      const cookieToken = ssoEntry.split("=")[1];
      apiClient.defaults.headers.common["Authorization"] = `Bearer ${cookieToken}`;
      apiClient
        .get("/api/auth/me")
        .then((res) => {
          syncToStore(cookieToken, res.data);
          window.location.href = "/";
        })
        .catch(() => {
          document.cookie = "ai_sso_token=; Max-Age=0; path=/; SameSite=Lax";
          redirectToNews();
        });
      return;
    }

    redirectToNews();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError("");

    if (password.length < 6) {
      setLocalError("密码至少需要 6 个字符");
      return;
    }

    const returnTo = new URLSearchParams(window.location.search).get("returnTo");
    const success = await register(email, password, nickname);
    if (success) {
      if (returnTo) {
        const { token, user } = useAuthStore.getState();
        const params = new URLSearchParams({ token: token || "", returnTo });
        if (user) {
          params.set("userId", user.id);
          params.set("email", user.email);
          params.set("nickname", user.nickname);
          params.set("role", user.role);
          if (user.avatar_url) params.set("avatar_url", user.avatar_url);
        }
        window.location.href = `${returnTo}?${params.toString()}`;
      } else {
        router.push("/");
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4">
      <div className="w-full max-w-md">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          返回首页
        </Link>

        <Card className="shadow-lg">
          <CardHeader className="space-y-1 text-center">
            <div className="flex justify-center mb-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground font-bold text-lg">
                AI
              </div>
            </div>
            <CardTitle className="text-2xl">创建账号</CardTitle>
            <CardDescription>注册 AI Writer，开始创作之旅</CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {(error || localError) && (
                <Alert variant="destructive">
                  <AlertDescription>{error || localError}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="nickname">昵称</Label>
                <div className="relative">
                  <LucideUser className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="nickname"
                    type="text"
                    placeholder="选择一个昵称"
                    value={nickname}
                    onChange={(e) => setNickname(e.target.value)}
                    className="pl-10"
                    required
                    minLength={2}
                    maxLength={100}
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">邮箱</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">密码</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="至少 6 个字符"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  disabled={isLoading}
                />
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                注册
              </Button>
            </form>
          </CardContent>

          <CardFooter className="flex flex-col">
            <p className="text-sm text-muted-foreground text-center">
              已有账号？{" "}
              <Link href="/auth/login" className="text-primary hover:underline font-medium">
                登录
              </Link>
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
