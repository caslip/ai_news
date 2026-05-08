"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  ExternalLink,
  Clock,
  Search,
  Loader2,
  Heart,
  BookOpen,
  Star,
  GitFork,
  FileText,
  ArrowUpRight,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";
import { getPapers, getPaperStats, Paper, PaperStats } from "@/lib/api";

// ── Types ────────────────────────────────────────────────────────────────────────

interface PaperStatsData {
  today_count: number;
  week_count: number;
  month_count: number;
  total_count: number;
}

// ── Helpers ──────────────────────────────────────────────────────────────────────

function formatNumber(num: number): string {
  if (num >= 10000) return (num / 10000).toFixed(1) + "w";
  if (num >= 1000) return (num / 1000).toFixed(1) + "k";
  return num.toString();
}

function getSourceBadge(paper: Paper): { label: string; color: string; bg: string; border: string } {
  if (paper.hf_paper_id) {
    return { label: "HuggingFace", color: "text-orange-500", bg: "bg-orange-500/10", border: "border-orange-500/30" };
  }
  if (paper.arxiv_id) {
    return { label: "arXiv", color: "text-blue-500", bg: "bg-blue-500/10", border: "border-blue-500/30" };
  }
  return { label: "Paper", color: "text-green-500", bg: "bg-green-500/10", border: "border-green-500/30" };
}

// ── Paper Card Component ─────────────────────────────────────────────────────────

function PaperCard({ paper }: { paper: Paper }) {
  const badge = getSourceBadge(paper);
  const hasThumbnail = !!paper.thumbnail_url;
  const hasGithub = !!paper.github_repo;
  const hasProjectPage = !!paper.project_page;

  return (
    <Card className="group hover:shadow-md transition-all duration-200 hover:border-green-500/30">
      <CardContent className="p-5">
        <div className="flex gap-4">
          {/* Thumbnail */}
          {hasThumbnail && (
            <div className="flex-shrink-0">
              <img
                src={paper.thumbnail_url!}
                alt={paper.title}
                className="w-20 h-20 object-cover rounded-lg border"
                onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
              />
            </div>
          )}

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Header Row */}
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex-1 min-w-0">
                {/* Badges Row */}
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <Badge
                    variant="outline"
                    className={`${badge.bg} ${badge.color} ${badge.border} border text-xs`}
                  >
                    <BookOpen className="h-3 w-3 mr-1" />
                    {badge.label}
                  </Badge>
                  {paper.primary_category && (
                    <Badge variant="secondary" className="text-xs">
                      {paper.primary_category}
                    </Badge>
                  )}
                  {paper.upvotes > 0 && (
                    <Badge variant="secondary" className="text-xs bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-400">
                      <Heart className="h-3 w-3 mr-1" />
                      {formatNumber(paper.upvotes)}
                    </Badge>
                  )}
                </div>

                {/* Title */}
                <a
                  href={paper.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block"
                >
                  <h3 className="text-base font-semibold leading-snug line-clamp-2 hover:text-green-600 dark:hover:text-green-400 transition-colors">
                    {paper.title}
                  </h3>
                </a>
              </div>

              {/* Upvotes Side */}
              {paper.upvotes > 0 && (
                <div className="flex flex-col items-center gap-1 text-center min-w-[50px] flex-shrink-0">
                  <Heart className="h-4 w-4 text-red-500" />
                  <span className="text-sm font-bold text-red-500">
                    {formatNumber(paper.upvotes)}
                  </span>
                </div>
              )}
            </div>

            {/* Summary */}
            {paper.summary && (
              <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                {paper.summary}
              </p>
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
                    {formatDistanceToNow(new Date(paper.published_at), {
                      addSuffix: true,
                      locale: zhCN,
                    })}
                  </span>
                </>
              )}
            </div>

            {/* Categories & Tags */}
            {paper.categories && paper.categories.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {paper.categories.slice(0, 8).map((cat) => (
                  <Badge key={cat} variant="outline" className="text-xs border-dashed">
                    {cat}
                  </Badge>
                ))}
                {paper.categories.length > 8 && (
                  <span className="text-xs text-muted-foreground">+{paper.categories.length - 8}</span>
                )}
              </div>
            )}

            {/* Actions Row */}
            <div className="flex items-center justify-between pt-2 border-t border-border/50">
              <div className="flex items-center gap-3">
                {/* Arxiv ID */}
                {paper.arxiv_id && (
                  <a
                    href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-blue-500 hover:underline"
                  >
                    <FileText className="h-3 w-3" />
                    arxiv:{paper.arxiv_id}
                  </a>
                )}

                {/* GitHub Repo */}
                {hasGithub && (
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

                {/* Project Page */}
                {hasProjectPage && (
                  <a
                    href={paper.project_page!}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-green-500 hover:underline"
                  >
                    <ArrowUpRight className="h-3 w-3" />
                    Project
                  </a>
                )}
              </div>

              {/* External Link */}
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

// ── Stats Cards ─────────────────────────────────────────────────────────────────

function PaperStatsCards({ stats }: { stats?: PaperStatsData }) {
  if (!stats) return null;
  const items = [
    { label: "今日新增", value: stats.today_count, color: "text-green-500" },
    { label: "本周新增", value: stats.week_count, color: "text-blue-500" },
    { label: "本月新增", value: stats.month_count, color: "text-orange-500" },
    { label: "论文总数", value: stats.total_count, color: "text-purple-500" },
  ];

  return (
    <div className="grid grid-cols-4 gap-4">
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

// ── Main Page ────────────────────────────────────────────────────────────────────

export default function PapersPage() {
  const [sourceType, setSourceType] = useState("");
  const [category, setCategory] = useState("");
  const [minUpvotes, setMinUpvotes] = useState("");
  const [timeRange, setTimeRange] = useState("today");
  const [sort, setSort] = useState("time");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);

  // Fetch papers
  const { data: papersData, isLoading, refetch } = useQuery({
    queryKey: ["papers", sourceType, category, minUpvotes, timeRange, sort, searchQuery, page],
    queryFn: async () => {
      try {
        const params: Record<string, string | number> = { page, page_size: 20 };
        if (sourceType) params.source_type = sourceType;
        if (category) params.category = category;
        if (minUpvotes) params.min_upvotes = parseInt(minUpvotes);
        if (timeRange) params.time_range = timeRange;
        if (sort) params.sort = sort;
        if (searchQuery) params.q = searchQuery;
        return await getPapers(params);
      } catch (error) {
        console.error("Failed to fetch papers:", error);
        return { items: [], total: 0, page: 1, page_size: 20 };
      }
    },
  });

  // Fetch stats
  const { data: statsData } = useQuery({
    queryKey: ["papers-stats"],
    queryFn: async () => {
      try {
        return await getPaperStats();
      } catch (error) {
        console.error("Failed to fetch paper stats:", error);
        return undefined;
      }
    },
  });

  const papers = papersData?.items ?? [];
  const total = papersData?.total ?? 0;
  const totalPages = Math.ceil(total / 20);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <BookOpen className="h-6 w-6 text-green-500" />
                学术论文
              </h1>
              <p className="text-sm text-muted-foreground">
                追踪最新 AI 领域学术论文 · Arxiv &amp; HuggingFace Papers
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 container mx-auto px-6 py-6 space-y-6">
        {/* Stats */}
        <PaperStatsCards stats={statsData} />

        {/* Filter Bar */}
        <Card>
          <CardContent className="pt-4 pb-4">
            <div className="flex flex-col lg:flex-row gap-3">
              {/* Search */}
              <div className="relative flex-1 min-w-0">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="搜索论文标题或作者..."
                  value={searchQuery}
                  onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
                  className="pl-9 h-9"
                />
              </div>

              {/* Filter selects */}
              <div className="flex items-center gap-2 flex-shrink-0 flex-wrap">
                {/* Source Type */}
                <select
                  value={sourceType}
                  onChange={(e) => { setSourceType(e.target.value); setPage(1); }}
                  className="h-9 px-3 pr-8 rounded-md border border-input bg-background text-xs text-foreground cursor-pointer transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-ring appearance-none hover:border-ring/50"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                    backgroundPosition: 'right 0.5rem center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: '1.5em 1.5em',
                  }}
                >
                  <option value="">全部来源</option>
                  <option value="arxiv">arXiv</option>
                  <option value="hf_paper">HuggingFace</option>
                </select>

                {/* Category */}
                <select
                  value={category}
                  onChange={(e) => { setCategory(e.target.value); setPage(1); }}
                  className="h-9 px-3 pr-8 rounded-md border border-input bg-background text-xs text-foreground cursor-pointer transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-ring appearance-none hover:border-ring/50"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                    backgroundPosition: 'right 0.5rem center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: '1.5em 1.5em',
                  }}
                >
                  <option value="">全部分类</option>
                  <option value="cs.AI">cs.AI</option>
                  <option value="cs.CL">cs.CL</option>
                  <option value="cs.CV">cs.CV</option>
                  <option value="cs.LG">cs.LG</option>
                  <option value="cs.RO">cs.RO</option>
                  <option value="cs.NE">cs.NE</option>
                </select>

                {/* Min Upvotes */}
                <select
                  value={minUpvotes}
                  onChange={(e) => { setMinUpvotes(e.target.value); setPage(1); }}
                  className="h-9 px-3 pr-8 rounded-md border border-input bg-background text-xs text-foreground cursor-pointer transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-ring appearance-none hover:border-ring/50"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                    backgroundPosition: 'right 0.5rem center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: '1.5em 1.5em',
                  }}
                >
                  <option value="">全部点赞</option>
                  <option value="10">≥ 10</option>
                  <option value="50">≥ 50</option>
                  <option value="100">≥ 100</option>
                  <option value="500">≥ 500</option>
                </select>

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
                  value={sort}
                  onChange={(e) => { setSort(e.target.value); setPage(1); }}
                  className="h-9 px-3 pr-8 rounded-md border border-input bg-background text-xs text-foreground cursor-pointer transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-ring appearance-none hover:border-ring/50"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                    backgroundPosition: 'right 0.5rem center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: '1.5em 1.5em',
                  }}
                >
                  <option value="time">最新</option>
                  <option value="upvotes">热度</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results Header */}
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            共找到 <span className="font-semibold text-foreground">{total.toLocaleString()}</span> 篇论文
          </p>
        </div>

        {/* Papers List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : papers.length === 0 ? (
          <Card className="py-12">
            <CardContent className="text-center">
              <BookOpen className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">暂无论文</h3>
              <p className="text-sm text-muted-foreground">
                调整筛选条件或稍后再试
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {papers.map((paper) => (
              <PaperCard key={paper.id} paper={paper} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center gap-2 mt-6">
            <Button
              variant="outline"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              上一页
            </Button>
            <span className="flex items-center px-4">
              {page} / {totalPages}
            </span>
            <Button
              variant="outline"
              onClick={() => setPage((p) => p + 1)}
              disabled={page >= totalPages}
            >
              下一页
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
