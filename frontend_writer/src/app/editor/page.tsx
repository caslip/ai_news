"use client";

import { useEffect, useState, useCallback, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Copy,
  Download,
  Save,
  ArrowLeft,
  Loader2,
  Maximize2,
  Minimize2,
} from "lucide-react";
import { ArticleEditor } from "@/components/writer/ArticleEditor";
import { useAuthStore } from "@/stores/authStore";
import {
  loadEditorSession,
  getLastEditorKey,
  markdownToHtml,
} from "@/lib/editorSession";
import { toast } from "sonner";

function EditorContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { token, user, hasHydrated } = useAuthStore();

  const key = searchParams.get("key");

  /** Content set after markdown parsing — empty string = still loading */
  const [initialContent, setInitialContent] = useState("");
  /** Current editor content (user edits) */
  const [content, setContent] = useState("");
  const [title, setTitle] = useState("");
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Auth guard
  useEffect(() => {
    if (!hasHydrated) return;
    if (!token || !user) {
      router.push("/auth/login");
    }
  }, [hasHydrated, token, user, router]);

  // Load session — parse markdown async, update content only when ready
  useEffect(() => {
    const sessionKey = key || getLastEditorKey();
    if (!sessionKey) return;

    const session = loadEditorSession(sessionKey);
    if (!session) {
      if (key) toast.error("无法加载编辑器内容");
      return;
    }

    void markdownToHtml(session.content).then((html) => {
      setTitle(session.title || "");
      setInitialContent(html);
      setContent(html);
    });
  }, [key]);

  const handleEditorChange = useCallback((html: string) => {
    setContent(html);
  }, []);

  const handleCopy = () => {
    if (!content) return;
    const text = content.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
    navigator.clipboard.writeText(text);
    toast.success("已复制到剪贴板");
  };

  const handleDownload = () => {
    if (!content) return;
    const text = content.replace(/<[^>]+>/g, "\n").replace(/\n{3,}/g, "\n\n").trim();
    const blob = new Blob([`# ${title || "article"}\n\n${text}`], {
      type: "text/markdown",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title || "article"}.md`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("已下载 Markdown 文件");
  };

  const handleSaveToDraft = async () => {
    if (!content) return;
    const text = content.replace(/<[^>]+>/g, "\n").replace(/\n{3,}/g, "\n\n").trim();
    const wordCount = text.split(/\s+/).filter(Boolean).length;
    try {
      const { saveEditorSession, generateEditorKey } = await import("@/lib/editorSession");
      const k = key || generateEditorKey();
      saveEditorSession(k, {
        title,
        content: text,
        sourceContent: "",
        topic: "",
        style: "",
        tone: "",
        length: "",
      });
      toast.success(`已保存 ${wordCount} 字到草稿箱`);
    } catch {
      toast.error("保存失败");
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // Show skeleton while markdown is being parsed
  if (!initialContent && !content) {
    return (
      <div className="h-screen flex flex-col bg-background">
        <div className="flex items-center gap-4 px-6 py-3 border-b bg-card shrink-0">
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-6 w-48 ml-auto" />
        </div>
        <div className="flex-1 p-6">
          <Skeleton className="h-full w-full rounded-lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top bar */}
      <div className="flex items-center gap-4 px-6 py-3 border-b bg-card shrink-0">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/generate")}
          className="gap-1.5"
        >
          <ArrowLeft className="h-4 w-4" />
          返回生成
        </Button>

        <div className="flex-1">
          <Input
            placeholder="输入文章标题..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="font-bold text-lg border-none shadow-none px-0 h-auto bg-transparent focus-visible:ring-0"
          />
        </div>

        <div className="flex items-center gap-1.5">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            disabled={!content}
            className="gap-1.5"
          >
            <Copy className="h-3.5 w-3.5" />
            复制
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownload}
            disabled={!content}
            className="gap-1.5"
          >
            <Download className="h-3.5 w-3.5" />
            下载
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleSaveToDraft}
            disabled={!content}
            className="gap-1.5"
          >
            <Save className="h-3.5 w-3.5" />
            保存草稿
          </Button>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={toggleFullscreen}
            title={isFullscreen ? "退出全屏" : "全屏"}
          >
            {isFullscreen ? (
              <Minimize2 className="h-4 w-4" />
            ) : (
              <Maximize2 className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Editor area */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <ArticleEditor
          content={content}
          onChange={handleEditorChange}
          editable={true}
          className="h-full"
        />
      </div>
    </div>
  );
}

export default function EditorPage() {
  return (
    <Suspense
      fallback={
        <div className="h-screen flex items-center justify-center bg-background">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      }
    >
      <EditorContent />
    </Suspense>
  );
}
