"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  MoreHorizontal,
  Rss,
  Radio,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  Trash2,
  ExternalLink,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";

interface SourceHealth {
  id: string;
  name: string;
  type: string;
  url: string;
  is_active: boolean;
  last_fetched_at: string | null;
  last_error: string | null;
  success_count: number;
  error_count: number;
  success_rate: number;
  avg_response_time_ms: number;
  articles_count: number;
}

const sourceTypeIcons = {
  rss: Rss,
  twitter: Radio,
  github: RefreshCw,
};

const sourceTypeLabels = {
  rss: "RSS",
  twitter: "Twitter",
  github: "GitHub",
};

export default function SourceHealthPage() {
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<"all" | "active" | "inactive">("all");

  const { data: sources, isLoading } = useQuery({
    queryKey: ["admin-sources-health"],
    queryFn: async () => {
      const response = await apiClient.get<SourceHealth[]>("/api/admin/sources/health");
      return response.data;
    },
    refetchInterval: 60000,
  });

  const refreshMutation = useMutation({
    mutationFn: async (sourceId: string) => {
      await apiClient.post(`/api/admin/sources/${sourceId}/refresh`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-sources-health"] });
    },
  });

  const filteredSources = sources?.filter((source) => {
    if (filter === "active") return source.is_active;
    if (filter === "inactive") return !source.is_active;
    return true;
  });

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-48 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">信源健康</h1>
        <p className="text-gray-500">监控所有信源的抓取状态</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Rss className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{sources?.length || 0}</p>
                <p className="text-sm text-gray-500">总信源</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-50 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {sources?.filter((s) => s.is_active).length || 0}
                </p>
                <p className="text-sm text-gray-500">活跃</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-50 rounded-lg">
                <XCircle className="w-5 h-5 text-red-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {sources?.filter((s) => !s.is_active).length || 0}
                </p>
                <p className="text-sm text-gray-500">停用</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-50 rounded-lg">
                <Clock className="w-5 h-5 text-orange-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {sources?.filter((s) => s.last_error).length || 0}
                </p>
                <p className="text-sm text-gray-500">异常</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 筛选 */}
      <div className="flex gap-2">
        <Button
          variant={filter === "all" ? "default" : "outline"}
          size="sm"
          onClick={() => setFilter("all")}
        >
          全部
        </Button>
        <Button
          variant={filter === "active" ? "default" : "outline"}
          size="sm"
          onClick={() => setFilter("active")}
        >
          活跃
        </Button>
        <Button
          variant={filter === "inactive" ? "default" : "outline"}
          size="sm"
          onClick={() => setFilter("inactive")}
        >
          停用
        </Button>
      </div>

      {/* 信源表格 */}
      <Card>
        <CardHeader>
          <CardTitle>信源列表</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>信源</TableHead>
                <TableHead>类型</TableHead>
                <TableHead>状态</TableHead>
                <TableHead>文章数</TableHead>
                <TableHead>成功率</TableHead>
                <TableHead>最后抓取</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSources?.map((source) => {
                const Icon = sourceTypeIcons[source.type as keyof typeof sourceTypeIcons] || Rss;
                return (
                  <TableRow key={source.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{source.name}</p>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-500 hover:underline flex items-center gap-1"
                        >
                          {source.url.slice(0, 40)}
                          {source.url.length > 40 && "..."}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary" className="flex items-center gap-1 w-fit">
                        <Icon className="w-3 h-3" />
                        {sourceTypeLabels[source.type as keyof typeof sourceTypeLabels] || source.type}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {source.last_error ? (
                          <Badge variant="destructive" className="w-fit">
                            异常
                          </Badge>
                        ) : source.is_active ? (
                          <Badge variant="success" className="w-fit">
                            正常
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="w-fit">
                            停用
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{source.articles_count}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500 rounded-full"
                            style={{ width: `${source.success_rate}%` }}
                          ></div>
                        </div>
                        <span className="text-sm">{source.success_rate.toFixed(0)}%</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-gray-500">
                      {source.last_fetched_at
                        ? formatDistanceToNow(new Date(source.last_fetched_at), {
                            addSuffix: true,
                            locale: zhCN,
                          })
                        : "从未抓取"}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() => refreshMutation.mutate(source.id)}
                            disabled={refreshMutation.isPending}
                          >
                            <RefreshCw className="w-4 h-4 mr-2" />
                            立即抓取
                          </DropdownMenuItem>
                          <DropdownMenuItem asChild>
                            <a href="/sources" target="_blank">
                              <Rss className="w-4 h-4 mr-2" />
                              查看详情
                            </a>
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
