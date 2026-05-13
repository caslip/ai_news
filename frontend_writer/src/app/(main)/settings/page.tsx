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

const STYLE_OPTIONS = [
  { value: "technical", label: "技术解读" },
  { value: "news_analysis", label: "热点分析" },
  { value: "tutorial", label: "教程指南" },
  { value: "opinion", label: "观点评论" },
  { value: "product_review", label: "产品评测" },
];

const TONE_OPTIONS = [
  { value: "professional", label: "专业严谨" },
  { value: "casual", label: "轻松活泼" },
  { value: "concise", label: "简洁明了" },
  { value: "storytelling", label: "故事叙述" },
];

const LENGTH_OPTIONS = [
  { value: "short", label: "短篇 (~500字)" },
  { value: "medium", label: "中篇 (~1500字)" },
  { value: "long", label: "长篇 (~3000字)" },
];

export default function SettingsPage() {
  const [defaultStyle, setDefaultStyle] = useState("technical");
  const [defaultTone, setDefaultTone] = useState("professional");
  const [defaultLength, setDefaultLength] = useState("medium");
  const [autoSave, setAutoSave] = useState(true);
  const [streaming, setStreaming] = useState(false);

  const handleSave = () => {
    toast.success("设置已保存");
  };

  return (
    <div className="container mx-auto px-6 py-6 space-y-6 max-w-2xl">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold">设置</h1>
        <p className="text-muted-foreground text-sm mt-1">
          配置你的写作偏好和系统设置
        </p>
      </div>

      {/* Default Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>写作偏好</CardTitle>
          <CardDescription>
            设置默认的写作风格，这些设置将作为新文章的初始值
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>默认写作风格</Label>
            <Select value={defaultStyle} onValueChange={setDefaultStyle}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STYLE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>默认语气</Label>
            <Select value={defaultTone} onValueChange={setDefaultTone}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TONE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>默认篇幅</Label>
            <Select value={defaultLength} onValueChange={setDefaultLength}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LENGTH_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* System Settings */}
      <Card>
        <CardHeader>
          <CardTitle>系统设置</CardTitle>
          <CardDescription>
            配置编辑器的行为和功能开关
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>自动保存草稿</Label>
              <p className="text-sm text-muted-foreground">
                每 30 秒自动保存一次草稿
              </p>
            </div>
            <Switch checked={autoSave} onCheckedChange={setAutoSave} />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>流式输出</Label>
              <p className="text-sm text-muted-foreground">
                实时显示生成进度（需要后端支持 SSE）
              </p>
            </div>
            <Switch checked={streaming} onCheckedChange={setStreaming} />
          </div>
        </CardContent>
      </Card>

      {/* API Settings */}
      <Card>
        <CardHeader>
          <CardTitle>API 配置</CardTitle>
          <CardDescription>
            配置后端 API 连接地址
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="api-url">API 地址</Label>
            <Input
              id="api-url"
              placeholder="http://localhost:8001"
              defaultValue={process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}
            />
            <p className="text-xs text-muted-foreground">
              修改后需要刷新页面生效
            </p>
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
