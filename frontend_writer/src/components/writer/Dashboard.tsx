"use client";

import Link from "next/link";
import {
  PenLine,
  FileText,
  LayoutTemplate,
  Clock,
  FilePen,
  Link2,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { StatsCardSkeleton, DraftTableSkeleton } from "@/components/ui/skeleton";
import { useWriterStats, useDrafts } from "@/hooks/useWriter";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";

const statusMap = {
  generating: { label: "生成中", variant: "warning" as const },
  completed: { label: "已完成", variant: "success" as const },
  failed: { label: "已失败", variant: "destructive" as const },
};

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useWriterStats();
  const { data: draftsData, isLoading: draftsLoading } = useDrafts({ page_size: 5 });

  const recentDrafts = draftsData?.items ?? [];

  return (
    <div className="container mx-auto px-6 py-6 space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold">AI Writer</h1>
        <p className="text-muted-foreground text-sm mt-1">
          智能内容生成平台，快速创作高质量文章
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statsLoading ? (
          <>
            <StatsCardSkeleton />
            <StatsCardSkeleton />
            <StatsCardSkeleton />
            <StatsCardSkeleton />
          </>
        ) : (
          <>
            <Card>
              <CardContent className="p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm text-muted-foreground">今日生成</p>
                    <p className="text-2xl font-bold mt-1">{stats?.today_count ?? 0}</p>
                    <p className="text-xs text-muted-foreground mt-1">篇</p>
                  </div>
                  <div className="p-3 rounded-full bg-primary/10">
                    <PenLine className="h-5 w-5 text-primary" />
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm text-muted-foreground">草稿总数</p>
                    <p className="text-2xl font-bold mt-1">{stats?.total_drafts ?? 0}</p>
                    <p className="text-xs text-muted-foreground mt-1">篇</p>
                  </div>
                  <div className="p-3 rounded-full bg-blue-500/10">
                    <FileText className="h-5 w-5 text-blue-500" />
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm text-muted-foreground">累计字数</p>
                    <p className="text-2xl font-bold mt-1">
                      {stats?.total_words?.toLocaleString() ?? 0}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">字</p>
                  </div>
                  <div className="p-3 rounded-full bg-green-500/10">
                    <LayoutTemplate className="h-5 w-5 text-green-500" />
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm text-muted-foreground">平均耗时</p>
                    <p className="text-2xl font-bold mt-1">
                      {stats?.avg_duration_seconds ?? 0}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">秒/篇</p>
                  </div>
                  <div className="p-3 rounded-full bg-amber-500/10">
                    <Clock className="h-5 w-5 text-amber-500" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>快速开始</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Link href="/generate">
              <Button className="w-full h-20 flex flex-col gap-2">
                <FilePen className="h-6 w-6" />
                <span>新建文章</span>
              </Button>
            </Link>
            <Link href="/generate?source=url">
              <Button variant="outline" className="w-full h-20 flex flex-col gap-2">
                <Link2 className="h-6 w-6" />
                <span>从 URL 导入</span>
              </Button>
            </Link>
            <Link href="/templates">
              <Button variant="outline" className="w-full h-20 flex flex-col gap-2">
                <LayoutTemplate className="h-6 w-6" />
                <span>浏览模板</span>
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Recent Drafts */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>最近草稿</CardTitle>
          <Link href="/drafts">
            <Button variant="ghost" size="sm">查看全部</Button>
          </Link>
        </CardHeader>
        <CardContent>
          {draftsLoading ? (
            <DraftTableSkeleton rows={5} />
          ) : recentDrafts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <FileText className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <p className="text-muted-foreground">暂无草稿</p>
              <Link href="/generate" className="mt-4">
                <Button size="sm">创建第一篇</Button>
              </Link>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>标题</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>字数</TableHead>
                  <TableHead>创建时间</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentDrafts.map((draft) => {
                  const status = statusMap[draft.status];
                  return (
                    <TableRow key={draft.id}>
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
                            <Link href={`/drafts/${draft.id}`}>
                              <Button variant="ghost" size="sm">查看</Button>
                            </Link>
                          )}
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
    </div>
  );
}
