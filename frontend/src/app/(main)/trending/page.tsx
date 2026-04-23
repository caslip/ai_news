"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  TrendingUp,
  Heart,
  Repeat2,
  MessageSquare,
  Bookmark,
  ExternalLink,
  Clock,
  Users,
  Flame,
  Loader2,
  Zap,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";

interface Article {
  id: string;
  title: string;
  url: string;
  summary?: string;
  source_name: string;
  source_type: string;
  hot_score: number;
  fan_count: number;
  engagement?: {
    likes: number;
    retweets: number;
    comments: number;
  };
  published_at?: string;
  fetched_at: string;
}

interface ArticleListResponse {
  items: Article[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const mockTrendingArticles: Article[] = [
  {
    id: "1",
    title: "小型 AI 创业团队如何在 6 个月内实现月收入 10 万",
    url: "https://example.com/ai-startup",
    summary: "一个只有 3 个人的 AI 创业团队，分享他们如何在竞争激烈的市场中找到自己的位置，实现快速增长...",
    source_name: "@startupfounder",
    source_type: "twitter",
    hot_score: 92.3,
    fan_count: 1250,
    engagement: { likes: 890, retweets: 320, comments: 156 },
    published_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    fetched_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
  },
  {
    id: "2",
    title: "为什么我放弃了 Claude，转向 Gemini 2.0",
    url: "https://example.com/gemini-vs-claude",
    summary: "作为一个深度 Claude 用户，我花了三个月对比 Gemini 2.0 的实际体验...",
    source_name: "@devenv",
    source_type: "twitter",
    hot_score: 78.4,
    fan_count: 3200,
    engagement: { likes: 456, retweets: 123, comments: 89 },
    published_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
    fetched_at: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
  },
  {
    id: "3",
    title: "分享一个我用 AI 副业月入 3 万的方法",
    url: "https://example.com/side-hustle",
    summary: "不需要编程基础，只需要会写提示词。这是一个普通人的 AI 副业实战记录...",
    source_name: "@aikOL",
    source_type: "twitter",
    hot_score: 88.7,
    fan_count: 850,
    engagement: { likes: 1200, retweets: 450, comments: 280 },
    published_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
    fetched_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
  },
  {
    id: "4",
    title: "Llama 4 开源复现攻略：从零搭建本地大模型",
    url: "https://example.com/llama4-local",
    summary: "手把手教你如何在本地运行 Llama 4，包括环境配置、量化方法、推理优化...",
    source_name: "开发者日报",
    source_type: "rss",
    hot_score: 85.2,
    fan_count: 0,
    engagement: { likes: 320, retweets: 89, comments: 45 },
    published_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    fetched_at: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
  },
];

function formatNumber(num: number): string {
  if (num >= 10000) return (num / 10000).toFixed(1) + "w";
  if (num >= 1000) return (num / 1000).toFixed(1) + "k";
  return num.toString();
}

function TrendCard({ article, rank }: { article: Article; rank: number }) {
  const viralScore =
    article.fan_count > 0
      ? (
          ((article.engagement?.likes || 0) * 1 +
            (article.engagement?.retweets || 0) * 3 +
            (article.engagement?.comments || 0) * 2) /
          article.fan_count *
          1000
        ).toFixed(1)
      : "N/A";

  return (
    <Card className="group hover:shadow-lg transition-all duration-300 hover:border-amber-500/50 overflow-hidden">
      <div className="flex">
        {/* Rank */}
        <div className="flex items-center justify-center w-12 bg-gradient-to-b from-amber-500/20 to-amber-500/5 border-r">
          <span className="text-2xl font-bold text-amber-600">#{rank}</span>
        </div>

        <div className="flex-1">
          <CardHeader className="pb-2">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-500/30 text-xs">
                    <Zap className="h-3 w-3 mr-1" />
                    低粉爆文
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {article.source_type === "twitter" ? "X / Twitter" : article.source_type.toUpperCase()}
                  </Badge>
                  <span className="text-xs text-muted-foreground">{article.source_name}</span>
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

              <div className="flex flex-col items-center gap-1 bg-gradient-to-b from-amber-500/10 to-transparent px-3 py-2 rounded-lg">
                <Flame className="h-5 w-5 text-amber-500" />
                <span className="text-lg font-bold text-amber-600">{article.hot_score.toFixed(1)}</span>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-3">
            {article.summary && (
              <p className="text-sm text-muted-foreground line-clamp-2">
                {article.summary}
              </p>
            )}

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4 p-3 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5 text-amber-600">
                  <TrendingUp className="h-4 w-4" />
                  <span className="text-sm font-medium">爆文指数</span>
                </div>
                <span className="text-lg font-bold text-amber-600">{viralScore}</span>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5 text-muted-foreground">
                  <Users className="h-4 w-4" />
                  <span className="text-sm">粉丝</span>
                </div>
                <span className="text-sm font-medium">
                  {article.fan_count > 0 ? formatNumber(article.fan_count) : "-"}
                </span>
              </div>

              {article.engagement && (
                <>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Heart className="h-3 w-3 text-rose-500" />
                      {formatNumber(article.engagement.likes)}
                    </span>
                    <span className="flex items-center gap-1">
                      <Repeat2 className="h-3 w-3 text-green-500" />
                      {formatNumber(article.engagement.retweets)}
                    </span>
                    <span className="flex items-center gap-1">
                      <MessageSquare className="h-3 w-3 text-blue-500" />
                      {formatNumber(article.engagement.comments)}
                    </span>
                  </div>
                </>
              )}
            </div>

            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                {article.published_at && (
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatDistanceToNow(new Date(article.published_at), {
                      addSuffix: true,
                      locale: zhCN,
                    })}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-1">
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Bookmark className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
                  <a href={article.url} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </Button>
              </div>
            </div>
          </CardContent>
        </div>
      </div>
    </Card>
  );
}

export default function TrendingPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["trending"],
    queryFn: async () => {
      try {
        const response = await apiClient.get("/api/articles/trending");
        return response.data;
      } catch (error) {
        console.error("Failed to fetch trending articles:", error);
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

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-amber-500" />
                低粉爆文
              </h1>
              <p className="text-sm text-muted-foreground">
                发现高价值但未被广泛传播的内容
              </p>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-500/30">
                <Zap className="h-3 w-3 mr-1" />
                AI 驱动筛选
              </Badge>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 container mx-auto px-6 py-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="space-y-4">
            {/* Info Card */}
            <Card className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-amber-500/20">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-amber-500/20 rounded-lg">
                    <TrendingUp className="h-5 w-5 text-amber-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-amber-600 mb-1">什么是低粉爆文？</h3>
                    <p className="text-sm text-muted-foreground">
                      粉丝数较低但互动数据优秀的优质内容。爆文指数 = (点赞 + 转发×3 + 评论×2) / 粉丝数 × 1000，
                      结合 AI 质量评分筛选而出。
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Article List */}
            {data?.items.map((article, index) => (
              <TrendCard key={article.id} article={article} rank={index + 1} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
