"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
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
  Copy,
  Download,
  RefreshCw,
  Link2,
  FileText,
  AlertCircle,
} from "lucide-react";
import { useGenerateContent } from "@/hooks/useWriter";
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

function GenerateContent() {
  const searchParams = useSearchParams();
  const sourceFromUrl = searchParams.get("source") === "url";

  const [sourceUrl, setSourceUrl] = useState("");
  const [sourceContent, setSourceContent] = useState("");
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("technical");
  const [tone, setTone] = useState("professional");
  const [length, setLength] = useState<"short" | "medium" | "long">("medium");
  const [output, setOutput] = useState("");
  const [outputTitle, setOutputTitle] = useState("");
  const [inputMode, setInputMode] = useState<"url" | "content">(
    sourceFromUrl ? "url" : "content"
  );

  const generateMutation = useGenerateContent();

  const handleGenerate = async () => {
    if (inputMode === "url" && !sourceUrl) {
      toast.error("请输入源 URL");
      return;
    }
    if (inputMode === "content" && !sourceContent) {
      toast.error("请输入内容素材");
      return;
    }

    setOutput("");
    setOutputTitle("");

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
        setOutput(result.content || "");
        setOutputTitle(result.title || "");
        toast.success("文章生成完成");
      } else if (result.status === "failed") {
        toast.error(result.error_message || "生成失败");
      }
    } catch {
      toast.error("生成失败，请重试");
    }
  };

  const handleCopy = () => {
    if (!output) return;
    navigator.clipboard.writeText(output);
    toast.success("已复制到剪贴板");
  };

  const handleDownload = () => {
    if (!output) return;
    const blob = new Blob([`# ${outputTitle}\n\n${output}`], {
      type: "text/markdown",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${outputTitle || "article"}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const isLoading = generateMutation.isPending;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left Panel - Input */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>输入</CardTitle>
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
                className="min-h-[200px]"
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

      {/* Right Panel - Output */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>输出</CardTitle>
            {output && (
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={handleCopy}>
                  <Copy className="h-4 w-4 mr-1" />
                  复制
                </Button>
                <Button variant="outline" size="sm" onClick={handleDownload}>
                  <Download className="h-4 w-4 mr-1" />
                  下载
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
            </div>
          ) : output ? (
            <div className="space-y-4">
              {outputTitle && (
                <h2 className="text-xl font-bold">{outputTitle}</h2>
              )}
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <div className="whitespace-pre-wrap text-sm leading-relaxed">
                  {output}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <FileText className="h-12 w-12 text-muted-foreground/30 mb-4" />
              <p className="text-muted-foreground text-sm">
                输入素材后点击「开始生成」<br />
                AI 将在这里输出文章内容
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function GeneratePage() {
  return (
    <div className="container mx-auto px-6 py-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">文章生成</h1>
        <p className="text-muted-foreground text-sm mt-1">
          输入素材或链接，AI 将为你生成优质内容
        </p>
      </div>
      <Suspense fallback={
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card><CardContent className="p-6 space-y-4"><Skeleton className="h-9 w-full" /><Skeleton className="h-9 w-full" /><Skeleton className="h-32 w-full" /></CardContent></Card>
          <Card><CardContent className="p-6 space-y-4"><Skeleton className="h-6 w-32" /><Skeleton className="h-64 w-full" /></CardContent></Card>
        </div>
      }>
        <GenerateContent />
      </Suspense>
    </div>
  );
}
