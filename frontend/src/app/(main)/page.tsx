"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  MessageSquare,
  Heart,
  Repeat2,
  Bookmark,
  ExternalLink,
  Clock,
  TrendingUp,
  Flame,
  Search,
  Filter,
  Loader2,
  Star,
  GitFork,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";
import { useAuthStore } from "@/stores/authStore";

// Types
interface Article {
  id: string;
  title: string;
  url: string;
  summary?: string;
  source_name: string;
  source_type: string;
  hot_score: number;
  is_low_fan_viral: boolean;
  tags: string[];
  author?: string;
  engagement?: {
    likes: number;
    retweets: number;
    comments: number;
  };
  raw_metadata?: {
    language?: string;
    stars?: number;
    forks?: number;
    stars_today?: number;
    [key: string]: any;
  };
  published_at?: string;
  fetched_at: string;
  is_bookmarked?: boolean;
}

// GitHub Trending 类型
interface GitHubTrendingRepo {
  rank: number;
  owner: string;
  repo: string;
  url: string;
  description: string;
  language: string | null;
  language_color: string | null;
  stars: number;
  stars_today: number;
  forks: number;
  built_by: string[];
}

interface GitHubTrendingResponse {
  repos: GitHubTrendingRepo[];
  fetched_at: string;
  language: string | null;
  since: string;
}

interface ArticleListResponse {
  items: Article[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface Stats {
  today_count: number;
  week_count: number;
  month_count: number;
}

// Source type icon/color mapping
const sourceTypeConfig: Record<string, { color: string; bg: string }> = {
  rss: { color: "text-orange-500", bg: "bg-orange-500/10" },
  twitter: { color: "text-sky-500", bg: "bg-sky-500/10" },
  github: { color: "text-purple-500", bg: "bg-purple-500/10" },
};

// Format number helper
function formatNumber(num: number): string {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + "w";
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + "k";
  }
  return num.toString();
}

// GitHub Trending Card Component
function GitHubTrendingCard({ repo, rank }: { repo: GitHubTrendingRepo; rank?: number }) {
  const languageColors: Record<string, string> = {
    Python: "bg-yellow-400",
    TypeScript: "bg-blue-400",
    JavaScript: "bg-yellow-500",
    Go: "bg-cyan-400",
    Rust: "bg-orange-500",
    Java: "bg-red-500",
    "C++": "bg-pink-400",
    C: "bg-gray-400",
    Ruby: "bg-red-600",
    Swift: "bg-orange-400",
    Kotlin: "bg-purple-500",
    Dart: "bg-blue-500",
    PHP: "bg-indigo-400",
    HTML: "bg-orange-400",
    CSS: "bg-blue-300",
  };

  const langColor = languageColors[repo.language || ""] || "bg-gray-400";

  return (
    <Card className="group hover:shadow-md transition-all duration-200 hover:border-primary/50 border-purple-200">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Badge variant="outline" className="bg-purple-500/10 text-purple-500 border-purple-500/30 text-xs">
                <svg className="h-3 w-3 mr-1" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                </svg>
                TRENDING
              </Badge>
              <span className="text-xs text-muted-foreground font-mono">{repo.owner}/{repo.repo}</span>
              {repo.language && (
                <span className="flex items-center gap-1 text-xs">
                  <span className={`w-2 h-2 rounded-full ${langColor}`}></span>
                  {repo.language}
                </span>
              )}
            </div>
            <CardTitle className="text-base leading-snug line-clamp-2">
              <a
                href={repo.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
              >
                {repo.owner}/{repo.repo}
              </a>
            </CardTitle>
          </div>
          {rank !== undefined && (
            <div className="flex flex-col items-center gap-1 text-center min-w-[50px]">
              <TrendingUp className="h-4 w-4 text-purple-500" />
              <span className="text-sm font-semibold text-purple-500">
                #{rank}
              </span>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {repo.description && (
          <p className="text-sm text-muted-foreground line-clamp-2">
            {repo.description}
          </p>
        )}

        {/* GitHub 统计数据 */}
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Star className="h-3 w-3" />
            {repo.stars.toLocaleString()}
          </span>
          <span className="flex items-center gap-1">
            <GitFork className="h-3 w-3" />
            {repo.forks.toLocaleString()}
          </span>
          {repo.stars_today > 0 && (
            <span className="flex items-center gap-1 text-green-500">
              <TrendingUp className="h-3 w-3" />
              +{repo.stars_today.toLocaleString()} today
            </span>
          )}
        </div>

        {/* 构建者 */}
        {repo.built_by.length > 0 && (
          <div className="flex items-center gap-2 pt-1">
            <span className="text-xs text-muted-foreground">Built by</span>
            <div className="flex -space-x-1">
              {repo.built_by.slice(0, 5).map((user, i) => (
                <a
                  key={i}
                  href={`https://github.com/${user}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary hover:underline"
                >
                  @{user}
                </a>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Article Card Component
function ArticleCard({ article, onBookmark }: { article: Article; onBookmark?: (id: string) => void }) {
  const typeConfig = sourceTypeConfig[article.source_type] || sourceTypeConfig.rss;

  const isGitHub = article.source_type === "github";
  const meta = article.raw_metadata;

  return (
    <Card className="group hover:shadow-md transition-all duration-200 hover:border-primary/50">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Badge variant="outline" className={`${typeConfig.color} ${typeConfig.bg} border-0 text-xs`}>
                {isGitHub ? "GITHUB" : article.source_type.toUpperCase()}
              </Badge>
              <span className="text-xs text-muted-foreground font-mono">{article.source_name}</span>
              {isGitHub && meta?.language && (
                <Badge variant="secondary" className="text-xs">{meta.language}</Badge>
              )}
              {article.is_low_fan_viral && (
                <Badge variant="secondary" className="text-xs bg-amber-500/10 text-amber-600 hover:bg-amber-500/10">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  低粉爆文
                </Badge>
              )}
            </div>
            <CardTitle className="text-base leading-snug line-clamp-2">
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
              >
                {article.title}
              </a>
            </CardTitle>
          </div>
          <div className="flex flex-col items-center gap-1 text-center min-w-[50px]">
            <Flame className="h-4 w-4 text-orange-500" />
            <span className="text-sm font-semibold text-orange-500">
              {article.hot_score.toFixed(1)}
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {article.summary && (
          <p className="text-sm text-muted-foreground line-clamp-2">
            {article.summary}
          </p>
        )}

        {/* GitHub Trending metadata: language, stars, forks, stars today */}
        {isGitHub && meta && (
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            {meta.language && (
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                {meta.language}
              </span>
            )}
            {meta.stars !== undefined && (
              <span className="flex items-center gap-1">
                <span>★</span>
                {formatNumber(meta.stars)}
              </span>
            )}
            {meta.forks !== undefined && (
              <span className="flex items-center gap-1">
                <span>⑂</span>
                {formatNumber(meta.forks)}
              </span>
            )}
            {meta.stars_today !== undefined && meta.stars_today > 0 && (
              <span className="flex items-center gap-1 text-green-500">
                <TrendingUp className="h-3 w-3" />
                +{formatNumber(meta.stars_today)} today
              </span>
            )}
          </div>
        )}

        {/* Twitter / RSS engagement */}
        {!isGitHub && article.engagement && (
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Heart className="h-3 w-3" />
              {formatNumber(article.engagement.likes)}
            </span>
            <span className="flex items-center gap-1">
              <Repeat2 className="h-3 w-3" />
              {formatNumber(article.engagement.retweets)}
            </span>
            <span className="flex items-center gap-1">
              <MessageSquare className="h-3 w-3" />
              {formatNumber(article.engagement.comments)}
            </span>
          </div>
        )}

        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            {article.author && (
              <span className="max-w-[100px] truncate">{article.author}</span>
            )}
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatDistanceToNow(new Date(article.published_at || article.fetched_at), {
                addSuffix: true,
                locale: zhCN,
              })}
            </span>
          </div>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onBookmark?.(article.id)}
            >
              <Bookmark className={`h-4 w-4 ${article.is_bookmarked ? "fill-current" : ""}`} />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
              <a href={article.url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4" />
              </a>
            </Button>
          </div>
        </div>

        {article.tags && article.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1">
            {article.tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Stats Cards Component
function StatsCards({ stats }: { stats?: Stats }) {
  if (!stats) return null;
  
  const items = [
    { label: "今日新增", value: stats.today_count, color: "text-orange-500" },
    { label: "本周新增", value: stats.week_count, color: "text-blue-500" },
    { label: "本月新增", value: stats.month_count, color: "text-green-500" },
  ];

  return (
    <div className="grid grid-cols-3 gap-4">
      {items.map((item) => (
        <Card key={item.label}>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">
              <span className={item.color}>{item.value.toLocaleString()}</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">{item.label}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// Main Page Component
export default function HomePage() {
  const [timeRange, setTimeRange] = useState("today");
  const [sourceFilter, setSourceFilter] = useState("all");
  const [sortBy, setSortBy] = useState("hot");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);
  const { isAuthenticated } = useAuthStore();

  // 获取文章列表（数据库来源）
  const { data: articlesData, isLoading: articlesLoading, refetch } = useQuery({
    queryKey: ["articles", timeRange, sourceFilter, sortBy, searchQuery, page],
    queryFn: async () => {
      try {
        const params: Record<string, string | number> = {
          page,
          page_size: 20,
        };

        if (timeRange === "today") {
          params["time_range"] = "today";
        } else if (timeRange === "week") {
          params["time_range"] = "week";
        } else {
          params["time_range"] = "month";
        }

        if (sourceFilter !== "all") {
          params["source_type"] = sourceFilter;
        }

        if (sortBy === "time") {
          params["sort"] = "time";
        }

        if (searchQuery) {
          params["q"] = searchQuery;
        }

        const response = await apiClient.get<ArticleListResponse>("/api/articles", { params });
        return response.data;
      } catch (error) {
        console.error("Failed to fetch articles:", error);
        return {
          items: [],
          total: 0,
          page: 1,
          page_size: 20,
          total_pages: 0,
        } as ArticleListResponse;
      }
    },
  });

  // 获取统计数据
  const { data: statsData } = useQuery({
    queryKey: ["articles-stats"],
    queryFn: async () => {
      try {
        const response = await apiClient.get<Stats>("/api/articles/stats");
        return response.data;
      } catch (error) {
        console.error("Failed to fetch stats:", error);
        return undefined;
      }
    },
  });

  // 获取 GitHub Trending 数据 - 始终加载
  const { data: trendingData, isLoading: trendingLoading } = useQuery({
    queryKey: ["github-trending"],
    queryFn: async () => {
      try {
        const response = await apiClient.get<GitHubTrendingResponse>("/api/github/trending", {
          params: { limit: 10 },
        });
        return response.data;
      } catch (error) {
        console.error("Failed to fetch GitHub trending:", error);
        return {
          repos: [],
          fetched_at: new Date().toISOString(),
          language: null,
          since: "daily",
        } as GitHubTrendingResponse;
      }
    },
  });

  // 收藏文章
  const handleBookmark = async (articleId: string) => {
    if (!isAuthenticated) {
      window.location.href = "/auth/login";
      return;
    }

    try {
      await apiClient.post(`/api/favorites/${articleId}`);
      refetch();
    } catch (error) {
      console.error("Failed to bookmark:", error);
    }
  };

  // 判断是否显示 GitHub Trending
  const showTrending = sourceFilter === "all" || sourceFilter === "github";
  const isLoading = articlesLoading || (showTrending && trendingLoading);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold">热点资讯</h1>
              <p className="text-sm text-muted-foreground">
                发现最新的 AI 领域动态和热门开源项目
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 container mx-auto px-6 py-6">
        {/* Stats */}
        <StatsCards stats={statsData} />

        {/* Filters */}
        <Card className="mt-6">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="搜索资讯标题或内容..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>

              {/* Time Range */}
              <Select value={timeRange} onValueChange={(v) => { setTimeRange(v); setPage(1); }}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="时间范围" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="today">今日</SelectItem>
                  <SelectItem value="week">本周</SelectItem>
                  <SelectItem value="month">本月</SelectItem>
                </SelectContent>
              </Select>

              {/* Source Filter */}
              <Select value={sourceFilter} onValueChange={(v) => { setSourceFilter(v); setPage(1); }}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="信源" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部信源</SelectItem>
                  <SelectItem value="rss">RSS</SelectItem>
                  <SelectItem value="twitter">X / Twitter</SelectItem>
                  <SelectItem value="github">GitHub</SelectItem>
                  <SelectItem value="netter">Nitter</SelectItem>
                </SelectContent>
              </Select>

              {/* Sort */}
              <Select value={sortBy} onValueChange={(v) => { setSortBy(v); setPage(1); }}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="排序" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hot">热度排序</SelectItem>
                  <SelectItem value="time">时间排序</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Content List */}
        <div className="mt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="space-y-4">
              {/* GitHub Trending Section */}
              {showTrending && trendingData && trendingData.repos.length > 0 && (
                <>
                  {/* Trending Section Header */}
                  <div className="flex items-center gap-2 py-2">
                    <Badge variant="outline" className="bg-purple-500/10 text-purple-500 border-purple-500/30">
                      <svg className="h-3 w-3 mr-1" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                      </svg>
                      GitHub Trending
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      今日热门开源项目 · {new Date(trendingData.fetched_at).toLocaleString("zh-CN")}
                    </span>
                  </div>

                  {/* Trending Cards */}
                  {trendingData.repos.map((repo, index) => (
                    <GitHubTrendingCard
                      key={`${repo.owner}/${repo.repo}`}
                      repo={repo}
                      rank={index + 1}
                    />
                  ))}

                  {/* Divider */}
                  <div className="border-t my-6" />
                </>
              )}

              {/* Articles Section */}
              {articlesData?.items.length === 0 && !showTrending ? (
                <Card className="py-12">
                  <CardContent className="text-center">
                    <Filter className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium mb-2">暂无资讯</h3>
                    <p className="text-sm text-muted-foreground">
                      调整筛选条件或稍后再试
                    </p>
                  </CardContent>
                </Card>
              ) : (
                articlesData?.items.map((article) => (
                  <ArticleCard
                    key={article.id}
                    article={article}
                    onBookmark={handleBookmark}
                  />
                ))
              )}
            </div>
          )}
        </div>

        {/* Pagination */}
        {articlesData && articlesData.total_pages > 1 && (
          <div className="flex justify-center gap-2 mt-6">
            <Button
              variant="outline"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              上一页
            </Button>
            <span className="flex items-center px-4">
              {page} / {articlesData.total_pages}
            </span>
            <Button
              variant="outline"
              onClick={() => setPage(p => p + 1)}
              disabled={page >= articlesData.total_pages}
            >
              下一页
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
