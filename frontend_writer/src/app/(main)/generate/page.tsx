"use client";

import { Suspense, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Loader2,
  RefreshCw,
  Link2,
  FileText,
  AlertCircle,
} from "lucide-react";
import { useGenerateContent } from "@/hooks/useWriter";
import { useGenerateStore } from "@/stores/generateStore";
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

export default function GeneratePage() {
  const router = useRouter();
  const {
    sourceUrl, setSourceUrl,
    sourceContent, setSourceContent,
    topic, setTopic,
    style, setStyle,
    tone, setTone,
    length, setLength,
    inputMode, setInputMode,
    clearOutput,
  } = useGenerateStore();

  const generateMutation = useGenerateContent();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("source") === "url") {
      setInputMode("url");
    }
  }, [setInputMode]);

  const handleGenerate = async () => {
    if (inputMode === "url" && !sourceUrl) {
      toast.error("请输入源 URL");
      return;
    }
    if (inputMode === "content" && !sourceContent) {
      toast.error("请输入内容素材");
      return;
    }

    clearOutput();

    try {
      const result = await generateMutation.mutateAsync({
        source_url: inputMode === "url" ? sourceUrl : undefined,
        source_content: inputMode === "content" ? sourceContent : undefined,
        topic: topic || undefined,
        style,
        tone,
        length,
      });

      if (result.status === "completed") {
        if (result.content) {
          const { generateEditorKey, saveEditorSession } = await import("@/lib/editorSession");
          const key = generateEditorKey();
          const markdownContent = result.content;
          saveEditorSession(key, {
            title: result.title || "",
            content: markdownContent,
            originalMarkdown: markdownContent, // 保留原始 Markdown 用于无损复制
            sourceContent,
            topic,
            style,
            tone,
            length,
          });
          // Navigate to editor in current tab
          router.push(`/editor?key=${encodeURIComponent(key)}`);
        } else {
          toast.warning("生成完成，但内容为空");
        }
      } else if (result.status === "failed") {
        toast.error(result.error_message || "生成失败");
      } else if (result.status === "generating") {
        toast.info("内容生成中，稍后将出现在草稿箱");
      }
    } catch {
      toast.error("生成失败，请重试");
    }
  };

  const isLoading = generateMutation.isPending;

  return (
    <Suspense
      fallback={
        <Card>
          <CardContent className="p-6 space-y-4">
            <Skeleton className="h-9 w-full" />
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-9 w-full" />
          </CardContent>
        </Card>
      }
    >
      <div className="container mx-auto px-6 py-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold">文章生成</h1>
          <p className="text-muted-foreground text-sm mt-1">
            输入素材或链接，AI 将为你生成优质内容
          </p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>输入素材</CardTitle>
              <div className="flex gap-2">
                <Badge
                  variant={inputMode === "url" ? "default" : "secondary"}
                  className="cursor-pointer"
                  onClick={() => setInputMode("url")}
                >
                  <Link2 className="h-3 w-3 mr-1" />
                  URL
                </Badge>
                <Badge
                  variant={inputMode === "content" ? "default" : "secondary"}
                  className="cursor-pointer"
                  onClick={() => setInputMode("content")}
                >
                  <FileText className="h-3 w-3 mr-1" />
                  内容
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {inputMode === "url" ? (
              <div className="space-y-2">
                <Label htmlFor="url">源 URL</Label>
                <Input
                  id="url"
                  placeholder="https://example.com/article"
                  value={sourceUrl}
                  onChange={(e) => setSourceUrl(e.target.value)}
                />
              </div>
            ) : (
              <div className="space-y-2">
                <Label htmlFor="content">内容素材</Label>
                <Textarea
                  id="content"
                  placeholder="粘贴你想用来生成文章的素材内容..."
                  className="min-h-[240px]"
                  value={sourceContent}
                  onChange={(e) => setSourceContent(e.target.value)}
                />
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="topic">主题/关键词（可选）</Label>
              <Input
                id="topic"
                placeholder="例如：AI 大模型发展趋势"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label>写作风格</Label>
                <Select value={style} onValueChange={setStyle}>
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
                <Label>语气</Label>
                <Select value={tone} onValueChange={setTone}>
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
                <Label>篇幅</Label>
                <Select
                  value={length}
                  onValueChange={(v) => setLength(v as "short" | "medium" | "long")}
                >
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
            </div>

            <Button
              className="w-full"
              size="lg"
              onClick={handleGenerate}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  生成中...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  开始生成
                </>
              )}
            </Button>

            {generateMutation.isError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  生成失败，请检查输入或稍后重试
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      </div>
    </Suspense>
  );
}
