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
import { useAuthStore, type User } from "@/stores/authStore";

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error, clearError } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const [localError, setLocalError] = useState("");

  useEffect(() => {
    // Handle GitHub OAuth callback: token comes back in URL params
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    if (token) {
      const userId = params.get("userId") || params.get("id") || "";
      const userData: User = {
        id: userId,
        email: params.get("email") || "",
        nickname: params.get("nickname") || "",
        avatar_url: params.get("avatar_url") || undefined,
        role: (params.get("role") as "user" | "admin") || "user",
        push_config: {},
        created_at: "",
      };
      useAuthStore.setState({ token, user: userData, isAuthenticated: true });
      window.history.replaceState({}, "", window.location.pathname);
      router.push("/");
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError("");
    clearError();

    if (password.length < 8) {
      setLocalError("密码至少需要 8 个字符");
      return;
    }

    const success = await register(email, password, nickname);
    if (success) {
      router.push("/");
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
                  placeholder="至少 8 个字符"
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
