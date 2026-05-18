"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { ExternalLink, Key, Settings, AlertCircle } from "lucide-react";

export default function SettingsPage() {
  const [notifications, setNotifications] = useState(true);
  const [emailDigest, setEmailDigest] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const handleSave = () => {
    toast.success("设置已保存");
  };

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 max-w-2xl">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold">设置</h1>
        <p className="text-muted-foreground text-sm mt-1">
          配置你的个人偏好和通知设置
        </p>
      </div>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            通知偏好
          </CardTitle>
          <CardDescription>
            管理你的通知和提醒方式
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>推送通知</Label>
              <p className="text-sm text-muted-foreground">
                接收新资讯和热门内容的推送通知
              </p>
            </div>
            <Switch checked={notifications} onCheckedChange={setNotifications} />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>邮件摘要</Label>
              <p className="text-sm text-muted-foreground">
                每日接收精选资讯邮件摘要
              </p>
            </div>
            <Switch checked={emailDigest} onCheckedChange={setEmailDigest} />
          </div>
        </CardContent>
      </Card>

      {/* Feed Settings */}
      <Card>
        <CardHeader>
          <CardTitle>内容偏好</CardTitle>
          <CardDescription>
            自定义你的资讯浏览体验
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>自动刷新</Label>
              <p className="text-sm text-muted-foreground">
                页面自动刷新获取最新内容
              </p>
            </div>
            <Switch checked={autoRefresh} onCheckedChange={setAutoRefresh} />
          </div>
        </CardContent>
      </Card>

      {/* API Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            API 密钥配置
          </CardTitle>
          <CardDescription>
            管理 AI 服务提供商的 API 密钥
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-900 dark:bg-amber-950/30">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-amber-800 dark:text-amber-200">
                  在 AI Writer 中管理 API 密钥
                </p>
                <p className="text-sm text-amber-700/80 dark:text-amber-300/80 mt-1">
                  API 密钥配置功能集成在 AI Writer 平台中。请前往 AI Writer 进行管理。
                </p>
              </div>
            </div>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => window.open("http://localhost:3002/settings", "_blank")}
              className="flex items-center gap-2"
            >
              <ExternalLink className="h-4 w-4" />
              打开 AI Writer 设置
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            支持 DeepSeek、Kimi、MiniMax、OpenAI、Gemini、Anthropic、OpenRouter 等多个 AI 提供商
          </p>
        </CardContent>
      </Card>

      {/* System Settings */}
      <Card>
        <CardHeader>
          <CardTitle>系统信息</CardTitle>
          <CardDescription>
            查看系统版本和连接状态
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">后端 API</span>
            <span className="font-mono">http://localhost:8001</span>
          </div>
          <Separator />
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">版本</span>
            <span className="font-mono">1.0.0</span>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave}>保存设置</Button>
      </div>
    </div>
  );
}
