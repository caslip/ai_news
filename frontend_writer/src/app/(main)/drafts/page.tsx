"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertCircle,
  Trash2,
  Download,
  Eye,
  RefreshCw,
  FileText,
  X,
  ExternalLink,
} from "lucide-react";
import { useDrafts, useDeleteDraft, useBatchDeleteDrafts, useDraft } from "@/hooks/useWriter";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";
import type { Draft } from "@/lib/api";

const STATUS_FILTERS = [
  { value: "all", label: "全部" },
  { value: "generating", label: "生成中" },
  { value: "completed", label: "已完成" },
  { value: "failed", label: "失败" },
];

const statusMap = {
  generating: { label: "生成中", variant: "warning" as const },
  completed: { label: "已完成", variant: "success" as const },
  failed: { label: "已失败", variant: "destructive" as const },
};

export default function DraftsPage() {
  const [statusFilter, setStatusFilter] = useState("all");
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [page, setPage] = useState(1);
  const [viewDraft, setViewDraft] = useState<Draft | null>(null);

  const params = {
    status: statusFilter === "all" ? undefined : statusFilter,
    page,
    page_size: 10,
  };

  const { data, isLoading, isError, refetch } = useDrafts(params);
  const deleteMutation = useDeleteDraft();
  const batchDeleteMutation = useBatchDeleteDrafts();

  const drafts = data?.items ?? [];
  const total = data?.total ?? 0;

  const toggleSelect = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelectedIds(next);
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === drafts.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(drafts.map((d) => d.id)));
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteMutation.mutateAsync(id);
      toast.success("删除成功");
    } catch {
      toast.error("删除失败");
    }
  };

  const handleBatchDelete = async () => {
    if (selectedIds.size === 0) return;
    try {
      await batchDeleteMutation.mutateAsync(Array.from(selectedIds));
      setSelectedIds(new Set());
      toast.success("批量删除成功");
    } catch {
      toast.error("批量删除失败");
    }
  };

  const handleView = (draft: Draft) => {
    setViewDraft(draft);
  };

  const handleExport = (id: string, title: string) => {
    const draft = drafts.find((d) => d.id === id);
    if (!draft || !draft.content) {
      toast.error("无内容可导出");
      return;
    }
    const blob = new Blob([`# ${title || "article"}\n\n${draft.content}`], {
      type: "text/markdown",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title || "article"}.md`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("导出成功");
  };

  const handleExportViewDraft = () => {
    if (!viewDraft) return;
    handleExport(viewDraft.id, viewDraft.title);
  };

  return (
    <div className="container mx-auto px-6 py-6 space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold">草稿箱</h1>
        <p className="text-muted-foreground text-sm mt-1">
          管理你的所有文章草稿，共 {total} 篇
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-4">
        <div className="flex gap-2">
          {STATUS_FILTERS.map((f) => (
            <Button
              key={f.value}
              variant={statusFilter === f.value ? "default" : "outline"}
              size="sm"
              onClick={() => {
                setStatusFilter(f.value);
                setPage(1);
                setSelectedIds(new Set());
              }}
            >
              {f.label}
            </Button>
          ))}
        </div>
        <div className="flex-1" />
        {selectedIds.size > 0 && (
          <Button
            variant="destructive"
            size="sm"
            onClick={handleBatchDelete}
            disabled={batchDeleteMutation.isPending}
          >
            <Trash2 className="h-4 w-4 mr-1" />
            批量删除 ({selectedIds.size})
          </Button>
        )}
        <Button variant="outline" size="sm" onClick={() => void refetch()}>
          <RefreshCw className="h-4 w-4 mr-1" />
          刷新
        </Button>
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-4">
              <div className="flex gap-4 pb-3 border-b">
                <Skeleton className="h-4 w-4" />
                <Skeleton className="h-4 flex-1" />
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-20" />
              </div>
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex gap-4 items-center">
                  <Skeleton className="h-4 w-4" />
                  <Skeleton className="h-4 flex-1" />
                  <Skeleton className="h-5 w-16 rounded-full" />
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-24" />
                  <div className="flex gap-2">
                    <Skeleton className="h-7 w-14" />
                    <Skeleton className="h-7 w-14" />
                  </div>
                </div>
              ))}
            </div>
          ) : isError ? (
            <div className="p-6">
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>加载失败，请稍后重试</AlertDescription>
              </Alert>
            </div>
          ) : drafts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <FileText className="h-12 w-12 text-muted-foreground/30 mb-4" />
              <p className="text-muted-foreground">暂无草稿</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10">
                    <Checkbox
                      checked={
                        drafts.length > 0 && selectedIds.size === drafts.length
                      }
                      onCheckedChange={toggleSelectAll}
                    />
                  </TableHead>
                  <TableHead>标题</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>字数</TableHead>
                  <TableHead>创建时间</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {drafts.map((draft) => {
                  const status = statusMap[draft.status];
                  return (
                    <TableRow key={draft.id}>
                      <TableCell>
                        <Checkbox
                          checked={selectedIds.has(draft.id)}
                          onCheckedChange={() => toggleSelect(draft.id)}
                        />
                      </TableCell>
                      <TableCell className="font-medium max-w-[300px] truncate">
                        {draft.title || "无标题"}
                      </TableCell>
                      <TableCell>
                        <Badge variant={status.variant}>{status.label}</Badge>
                      </TableCell>
                      <TableCell>{draft.word_count}</TableCell>
                      <TableCell className="text-muted-foreground text-xs">
                        {formatDistanceToNow(new Date(draft.created_at), {
                          addSuffix: true,
                          locale: zhCN,
                        })}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          {draft.status === "completed" && (
                            <>
                              <Button
                                variant="ghost"
                                size="icon-sm"
                                onClick={() => handleView(draft)}
                                title="查看内容"
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon-sm"
                                onClick={() => handleExport(draft.id, draft.title)}
                                title="导出下载"
                              >
                                <Download className="h-4 w-4" />
                              </Button>
                            </>
                          )}
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => handleDelete(draft.id)}
                            title="删除草稿"
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {total > 10 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            第 {page} 页，共 {Math.ceil(total / 10)} 页
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              上一页
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= Math.ceil(total / 10)}
              onClick={() => setPage((p) => p + 1)}
            >
              下一页
            </Button>
          </div>
        </div>
      )}

      {/* View Draft Dialog */}
      <Dialog open={!!viewDraft} onOpenChange={(open) => !open && setViewDraft(null)}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader className="flex-shrink-0">
            <div className="flex items-center justify-between pr-8">
              <DialogTitle className="text-xl">
                {viewDraft?.title || "无标题"}
              </DialogTitle>
            </div>
            {viewDraft && (
              <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                <Badge variant="outline">{viewDraft.word_count} 字</Badge>
                <span>{viewDraft.style}</span>
                <span>{viewDraft.tone}</span>
                {viewDraft.source_url && (
                  <a
                    href={viewDraft.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-primary hover:underline"
                  >
                    <ExternalLink className="h-3 w-3" />
                    来源链接
                  </a>
                )}
              </div>
            )}
          </DialogHeader>
          <div className="flex-1 overflow-y-auto">
            {viewDraft?.status === "failed" ? (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  {viewDraft.error_message || "内容生成失败"}
                </AlertDescription>
              </Alert>
            ) : viewDraft?.status === "generating" ? (
              <div className="flex items-center justify-center py-12">
                <p className="text-muted-foreground">内容生成中...</p>
              </div>
            ) : (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <pre className="whitespace-pre-wrap text-sm leading-relaxed font-sans">
                  {viewDraft?.content || "暂无内容"}
                </pre>
              </div>
            )}
          </div>
          <div className="flex-shrink-0 flex justify-end gap-2 pt-4 border-t">
            <Button variant="outline" onClick={() => setViewDraft(null)}>
              关闭
            </Button>
            {viewDraft?.status === "completed" && viewDraft?.content && (
              <Button onClick={handleExportViewDraft}>
                <Download className="h-4 w-4 mr-2" />
                导出
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
