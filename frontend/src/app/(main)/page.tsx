"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient, getPapers, Paper } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { XTweetCard } from "@/components/XTweetCard";
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
  BookOpen,
  ArrowUpRight,
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

// Tab 配置
const TABS = [
  { id: "x", label: "X", color: "text-sky-500", bg: "bg-sky-500/10", border: "border-sky-500/30", hover: "hover:border-sky-500/50" },
  { id: "github", label: "GitHub", color: "text-purple-500", bg: "bg-purple-500/10", border: "border-purple-500/30", hover: "hover:border-purple-500/50" },
  { id: "rss", label: "RSS", color: "text-orange-500", bg: "bg-orange-500/10", border: "border-orange-500/30", hover: "hover:border-orange-500/50" },
  { id: "papers", label: "Papers", color: "text-green-500", bg: "bg-green-500/10", border: "border-green-500/30", hover: "hover:border-green-500/50" },
] as const;

type TabId = typeof TABS[number]["id"];

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
                {isGitHub ? "GITHUB" : (article.source_type?.toUpperCase() || "ARTICLE")}
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

        {/* GitHub Trending metadata */}
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

// Paper Card Component
function PaperCardInline({ paper }: { paper: Paper }) {
  const badge =
    paper.hf_paper_id
      ? { label: "HuggingFace", color: "text-orange-500", bg: "bg-orange-500/10", border: "border-orange-500/30" }
      : paper.arxiv_id
      ? { label: "arXiv", color: "text-blue-500", bg: "bg-blue-500/10", border: "border-blue-500/30" }
      : { label: "Paper", color: "text-green-500", bg: "bg-green-500/10", border: "border-green-500/30" };

  return (
    <Card className="group hover:shadow-md transition-all duration-200 hover:border-green-500/30">
      <CardContent className="p-5">
        <div className="flex gap-4">
          {/* Thumbnail */}
          {paper.thumbnail_url && (
            <div className="flex-shrink-0">
              <img
                src={paper.thumbnail_url}
                alt={paper.title}
                className="w-20 h-20 object-cover rounded-lg border"
                onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
              />
            </div>
          )}

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Badges + Title */}
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <Badge variant="outline" className={`${badge.bg} ${badge.color} ${badge.border} border text-xs`}>
                    <BookOpen className="h-3 w-3 mr-1" />
                    {badge.label}
                  </Badge>
                  {paper.primary_category && (
                    <Badge variant="secondary" className="text-xs">{paper.primary_category}</Badge>
                  )}
                  {paper.upvotes > 0 && (
                    <Badge variant="secondary" className="text-xs bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-400">
                      <Heart className="h-3 w-3 mr-1" />
                      {paper.upvotes >= 1000 ? (paper.upvotes / 1000).toFixed(1) + "k" : paper.upvotes}
                    </Badge>
                  )}
                </div>
                <a href={paper.url} target="_blank" rel="noopener noreferrer" className="block">
                  <h3 className="text-base font-semibold leading-snug line-clamp-2 hover:text-green-600 dark:hover:text-green-400 transition-colors">
                    {paper.title}
                  </h3>
                </a>
              </div>
              {paper.upvotes > 0 && (
                <div className="flex flex-col items-center gap-1 text-center min-w-[50px] flex-shrink-0">
                  <Heart className="h-4 w-4 text-red-500" />
                  <span className="text-sm font-bold text-red-500">
                    {paper.upvotes >= 1000 ? (paper.upvotes / 1000).toFixed(1) + "k" : paper.upvotes}
                  </span>
                </div>
              )}
            </div>

            {/* Summary */}
            {paper.summary && (
              <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{paper.summary}</p>
            )}

            {/* Author + Time */}
            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3">
              {paper.author && (
                <span className="max-w-[200px] truncate font-medium">{paper.author}</span>
              )}
              {paper.published_at && (
                <>
                  <span>·</span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatDistanceToNow(new Date(paper.published_at), { addSuffix: true, locale: zhCN })}
                  </span>
                </>
              )}
            </div>

            {/* Categories */}
            {paper.categories && paper.categories.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {paper.categories.slice(0, 6).map((cat) => (
                  <Badge key={cat} variant="outline" className="text-xs border-dashed">{cat}</Badge>
                ))}
                {paper.categories.length > 6 && (
                  <span className="text-xs text-muted-foreground">+{paper.categories.length - 6}</span>
                )}
              </div>
            )}

            {/* Actions Row */}
            <div className="flex items-center justify-between pt-2 border-t border-border/50">
              <div className="flex items-center gap-3">
                {paper.arxiv_id && (
                  <a
                    href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-blue-500 hover:underline"
                  >
                    <span className="font-mono">arxiv:{paper.arxiv_id}</span>
                  </a>
                )}
                {paper.github_repo && (
                  <a
                    href={`https://github.com/${paper.github_repo}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-purple-500 hover:underline"
                  >
                    <GitFork className="h-3 w-3" />
                    {paper.github_repo}
                  </a>
                )}
                {paper.project_page && (
                  <a
                    href={paper.project_page}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-green-500 hover:underline"
                  >
                    <ArrowUpRight className="h-3 w-3" />
                    Project
                  </a>
                )}
              </div>
              <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
                <a href={paper.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4" />
                </a>
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Main Page Component
export default function HomePage() {
  const [activeTab, setActiveTab] = useState<TabId>("x");
  const [timeRange, setTimeRange] = useState("today");
  const [sortBy, setSortBy] = useState("hot");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);
  const [paperPage, setPaperPage] = useState(1);
  const { isAuthenticated } = useAuthStore();

  // DEBUG: 检查环境变量 - 页面可见
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    console.log("[DEBUG] NEXT_PUBLIC_API_URL:", apiUrl);
    console.log("[DEBUG] apiClient baseURL:", apiClient.defaults.baseURL);
    document.title = `[DEBUG] ${apiUrl || "undefined"} | AI News`;
  }, []);

  // 根据 tab 确定 source_type 参数
  const sourceTypeMap: Record<TabId, string | undefined> = {
    x: "twitter,nitter",
    github: "github",
    rss: "rss",
    papers: undefined,
  };

  // 获取文章列表（数据库来源）
  const { data: articlesData, isLoading: articlesLoading, refetch } = useQuery({
    queryKey: ["articles", activeTab, timeRange, sortBy, searchQuery, page],
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

        const srcType = sourceTypeMap[activeTab];
        if (srcType) {
          params["source_type"] = srcType;
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

  // 获取 GitHub Trending 数据 - 仅 GitHub tab
  const { data: trendingData, isLoading: trendingLoading } = useQuery({
    queryKey: ["github-trending"],
    enabled: activeTab === "github",
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

  // 获取论文列表 - 仅 Papers tab
  const { data: papersData, isLoading: papersLoading } = useQuery({
    queryKey: ["papers-inline", paperPage],
    enabled: activeTab === "papers",
    queryFn: async () => {
      try {
        return await getPapers({ page: paperPage, page_size: 20 });
      } catch (error) {
        console.error("Failed to fetch papers:", error);
        return { items: [], total: 0, page: 1, page_size: 20 };
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
      await apiClient.post("/api/favorites/", {}, { params: { article_id: articleId } });
      refetch();
    } catch (error) {
      console.error("Failed to bookmark:", error);
    }
  };

  const isLoading = articlesLoading || (activeTab === "github" && trendingLoading) || (activeTab === "papers" && papersLoading);
  const items = articlesData?.items ?? [];
  const papers = papersData?.items ?? [];
  const papersTotal = papersData?.total ?? 0;
  const papersTotalPages = Math.ceil(papersTotal / 20);
  const hasData = items.length > 0 || (activeTab === "github" && (trendingData?.repos?.length ?? 0) > 0) || (activeTab === "papers" && papers.length > 0);

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

        {/* Tab + Filter Bar */}
        <Card className="sticky top-0 z-20 mt-6 backdrop-blur bg-card/80">
          <CardContent className="pt-4 pb-4">
            <div className="flex flex-col gap-3">
              {/* Tabs */}
              <div className="flex items-center gap-2 border-b pb-0">
                {TABS.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setActiveTab(tab.id);
                      setPage(1);
                    }}
                    className={`
                      relative px-4 py-2 text-sm font-medium transition-colors duration-150
                      ${activeTab === tab.id
                        ? `${tab.color}`
                        : "text-muted-foreground hover:text-foreground"
                      }
                    `}
                  >
                    {tab.label}
                    {activeTab === tab.id && (
                      <span className={`absolute bottom-0 left-0 right-0 h-0.5 ${tab.bg}`} />
                    )}
                  </button>
                ))}
              </div>

              {/* Filters row */}
              <div className="flex flex-col lg:flex-row gap-3">
                {/* Search */}
                <div className="relative flex-1 min-w-0">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="搜索资讯..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 h-9"
                  />
                </div>

                {/* Filter selects in one row */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  {/* Time Range */}
                  <select
                    value={timeRange}
                    onChange={(e) => { setTimeRange(e.target.value); setPage(1); }}
                    className="h-9 px-3 pr-8 rounded-md border border-input bg-background text-xs text-foreground cursor-pointer transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-ring appearance-none hover:border-ring/50"
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                      backgroundPosition: 'right 0.5rem center',
                      backgroundRepeat: 'no-repeat',
                      backgroundSize: '1.5em 1.5em',
                    }}
                  >
                    <option value="today">今日</option>
                    <option value="week">本周</option>
                    <option value="month">本月</option>
                  </select>

                  {/* Sort */}
                  <select
                    value={sortBy}
                    onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
                    className="h-9 px-3 pr-8 rounded-md border border-input bg-background text-xs text-foreground cursor-pointer transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-ring appearance-none hover:border-ring/50"
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                      backgroundPosition: 'right 0.5rem center',
                      backgroundRepeat: 'no-repeat',
                      backgroundSize: '1.5em 1.5em',
                    }}
                  >
                    <option value="hot">热度</option>
                    <option value="time">时间</option>
                  </select>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Content Area */}
        <div className="mt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : activeTab === "papers" ? (
            /* Papers Tab */
            <div className="space-y-4">
              {/* Papers List */}
              {papers.length === 0 ? (
                <Card className="py-12">
                  <CardContent className="text-center">
                    <BookOpen className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium mb-2">暂无论文</h3>
                    <p className="text-sm text-muted-foreground">暂无数据，稍后再试</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {papers.map((paper) => (
                    <PaperCardInline key={paper.id} paper={paper} />
                  ))}
                </div>
              )}
              {/* Pagination */}
              {papersTotalPages > 1 && (
                <div className="flex justify-center gap-2 mt-6">
                  <Button variant="outline" onClick={() => setPaperPage((p) => Math.max(1, p - 1))} disabled={paperPage === 1}>
                    上一页
                  </Button>
                  <span className="flex items-center px-4">
                    {paperPage} / {papersTotalPages}
                  </span>
                  <Button variant="outline" onClick={() => setPaperPage((p) => p + 1)} disabled={paperPage >= papersTotalPages}>
                    下一页
                  </Button>
                </div>
              )}
            </div>
          ) : activeTab === "github" && trendingData && trendingData.repos.length > 0 ? (
            /* GitHub Trending 模式 - 直接展示 cards */
            <div className="space-y-4">
              {/* Trending Header */}
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
            </div>
          ) : activeTab === "x" && items.length > 0 ? (
            /* X Tab - 使用 XTweetCard 展示 */
            <div className="space-y-4">
              {items.map((article) => (
                <XTweetCard
                  key={article.id}
                  tweet={article}
                  onBookmark={handleBookmark}
                />
              ))}
            </div>
          ) : hasData ? (
            /* RSS / 默认 - 使用 ArticleCard 展示 */
            <div className="space-y-4">
              {items.map((article) => (
                <ArticleCard
                  key={article.id}
                  article={article}
                  onBookmark={handleBookmark}
                />
              ))}
            </div>
          ) : (
            /* 无数据 */
            <Card className="py-12">
              <CardContent className="text-center">
                <Filter className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">暂无资讯</h3>
                <p className="text-sm text-muted-foreground">
                  调整筛选条件或稍后再试
                </p>
              </CardContent>
            </Card>
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
