"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Users,
  FileText,
  Rss,
  TrendingUp,
  Bookmark,
  Activity,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";
import { useEffect, useState } from "react";

interface AdminStats {
  total_users: number;
  total_articles: number;
  total_sources: number;
  active_sources: number;
  articles_today: number;
  articles_this_week: number;
  articles_this_month: number;
  low_fan_viral_count: number;
  bookmarks_count: number;
  active_strategies: number;
  queue_pending_tasks: number;
  queue_running_tasks: number;
  last_crawl_at: string | null;
  system_uptime: string;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: async () => {
      const response = await apiClient.get<AdminStats>("/api/admin/stats");
      return response.data;
    },
    refetchInterval: 30000,
  });

  useEffect(() => {
    if (data) {
      setStats(data);
    }
  }, [data]);

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-48 bg-gray-200 rounded"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-center gap-3 py-4">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <p className="text-red-700">加载管理面板失败，请检查权限</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const statCards = [
    {
      title: "总用户数",
      value: stats?.total_users || 0,
      icon: Users,
      color: "text-blue-500",
      bgColor: "bg-blue-50",
    },
    {
      title: "总文章数",
      value: stats?.total_articles || 0,
      icon: FileText,
      color: "text-green-500",
      bgColor: "bg-green-50",
    },
    {
      title: "活跃信源",
      value: `${stats?.active_sources || 0} / ${stats?.total_sources || 0}`,
      icon: Rss,
      color: "text-purple-500",
      bgColor: "bg-purple-50",
    },
    {
      title: "今日新增",
      value: stats?.articles_today || 0,
      icon: TrendingUp,
      color: "text-orange-500",
      bgColor: "bg-orange-50",
    },
    {
      title: "低粉爆文",
      value: stats?.low_fan_viral_count || 0,
      icon: Activity,
      color: "text-red-500",
      bgColor: "bg-red-50",
    },
    {
      title: "收藏总数",
      value: stats?.bookmarks_count || 0,
      icon: Bookmark,
      color: "text-pink-500",
      bgColor: "bg-pink-50",
    },
    {
      title: "活跃策略",
      value: stats?.active_strategies || 0,
      icon: CheckCircle,
      color: "text-teal-500",
      bgColor: "bg-teal-50",
    },
    {
      title: "等待任务",
      value: stats?.queue_pending_tasks || 0,
      icon: RefreshCw,
      color: "text-indigo-500",
      bgColor: "bg-indigo-50",
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">管理后台</h1>
          <p className="text-gray-500">系统概览与数据统计</p>
        </div>
        <button
          onClick={() => queryClient.invalidateQueries({ queryKey: ["admin-stats"] })}
          className="flex items-center gap-2 px-4 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50"
        >
          <RefreshCw className="w-4 h-4" />
          刷新
        </button>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <Card key={index}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{stat.title}</p>
                  <p className="text-2xl font-bold mt-1">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 文章统计 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>文章增长趋势</CardTitle>
            <CardDescription>各时间段文章数量</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                <span className="text-sm text-gray-600">今日</span>
                <span className="text-xl font-bold text-green-600">
                  {stats?.articles_today || 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                <span className="text-sm text-gray-600">本周</span>
                <span className="text-xl font-bold text-blue-600">
                  {stats?.articles_this_week || 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
                <span className="text-sm text-gray-600">本月</span>
                <span className="text-xl font-bold text-purple-600">
                  {stats?.articles_this_month || 0}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>系统状态</CardTitle>
            <CardDescription>最后抓取时间与运行状态</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">最后抓取</span>
                <span className="text-sm font-medium">
                  {stats?.last_crawl_at
                    ? formatDistanceToNow(new Date(stats.last_crawl_at), {
                        addSuffix: true,
                        locale: zhCN,
                      })
                    : "暂无"}
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">系统运行时间</span>
                <span className="text-sm font-medium">
                  {stats?.system_uptime || "N/A"}
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">运行中任务</span>
                <span className="text-sm font-medium">
                  {stats?.queue_running_tasks || 0} 个
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 快捷操作 */}
      <Card>
        <CardHeader>
          <CardTitle>快捷操作</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <a
              href="/admin/users"
              className="flex flex-col items-center gap-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <Users className="w-6 h-6 text-gray-600" />
              <span className="text-sm">用户管理</span>
            </a>
            <a
              href="/admin/sources"
              className="flex flex-col items-center gap-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <Rss className="w-6 h-6 text-gray-600" />
              <span className="text-sm">信源管理</span>
            </a>
            <a
              href="/sources"
              className="flex flex-col items-center gap-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <CheckCircle className="w-6 h-6 text-gray-600" />
              <span className="text-sm">信源健康</span>
            </a>
            <a
              href="/strategies"
              className="flex flex-col items-center gap-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <Activity className="w-6 h-6 text-gray-600" />
              <span className="text-sm">策略管理</span>
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
