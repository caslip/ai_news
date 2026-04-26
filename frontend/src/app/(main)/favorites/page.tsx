"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Bookmark,
  Search,
  Tag,
  Plus,
  Trash2,
  ExternalLink,
  Clock,
  Loader2,
  FolderOpen,
} from "lucide-react";

interface Tag {
  id: string;
  name: string;
  color: string;
}

interface Article {
  id: string;
  title: string;
  url: string;
  summary?: string;
  author?: string;
  hot_score: number;
  tags: string[];
  fetched_at: string;
}

interface Bookmark {
  id: string;
  article_id: string;
  article: Article;
  tags: Tag[];
  created_at: string;
}

const mockTags: Tag[] = [
  { id: "1", name: "LLM", color: "#3b82f6" },
  { id: "2", name: "开源", color: "#22c55e" },
  { id: "3", name: "创业", color: "#f59e0b" },
  { id: "4", name: "教程", color: "#8b5cf6" },
  { id: "5", name: "工具", color: "#ec4899" },
];

// 使用固定日期避免 hydration mismatch
const FIXED_NOW = "2026-04-25T10:00:00.000Z";

const mockBookmarks: Bookmark[] = [
  {
    id: "1",
    article_id: "1",
    article: {
      id: "1",
      title: "GPT-5 发布：AGI 之路的重要里程碑",
      url: "https://example.com/gpt5",
      summary: "OpenAI 正式发布 GPT-5，带来了前所未有的推理能力...",
      author: "@sama",
      hot_score: 98.5,
      tags: ["LLM", "OpenAI"],
      fetched_at: new Date(new Date(FIXED_NOW).getTime() - 1000 * 60 * 60 * 2).toISOString(),
    },
    tags: [mockTags[0]],
    created_at: new Date(new Date(FIXED_NOW).getTime() - 1000 * 60 * 60 * 3).toISOString(),
  },
  {
    id: "2",
    article_id: "2",
    article: {
      id: "2",
      title: "Llama 4 开源：Meta 再次改变游戏规则",
      url: "https://example.com/llama4",
      summary: "Meta 发布了 Llama 4 开源模型...",
      author: "zuck",
      hot_score: 96.8,
      tags: ["LLM", "开源"],
      fetched_at: new Date(new Date(FIXED_NOW).getTime() - 1000 * 60 * 60 * 5).toISOString(),
    },
    tags: [mockTags[0], mockTags[1]],
    created_at: new Date(new Date(FIXED_NOW).getTime() - 1000 * 60 * 60 * 6).toISOString(),
  },
  {
    id: "3",
    article_id: "3",
    article: {
      id: "3",
      title: "小型 AI 创业团队如何在 6 个月内实现月收入 10 万",
      url: "https://example.com/startup",
      summary: "一个只有 3 个人的 AI 创业团队...",
      author: "@startupfounder",
      hot_score: 92.3,
      tags: ["创业"],
      fetched_at: new Date(new Date(FIXED_NOW).getTime() - 1000 * 60 * 60 * 8).toISOString(),
    },
    tags: [mockTags[2]],
    created_at: new Date(new Date(FIXED_NOW).getTime() - 1000 * 60 * 60 * 10).toISOString(),
  },
];

export default function FavoritesPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [isAddTagDialogOpen, setIsAddTagDialogOpen] = useState(false);
  const [newTagName, setNewTagName] = useState("");
  const queryClient = useQueryClient();

  const { data: bookmarks, isLoading } = useQuery({
    queryKey: ["favorites", selectedTag],
    queryFn: async () => {
      await new Promise((r) => setTimeout(r, 300));
      return mockBookmarks;
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await new Promise((r) => setTimeout(r, 300));
      return id;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["favorites"] }),
  });

  const createTagMutation = useMutation({
    mutationFn: async (name: string) => {
      await new Promise((r) => setTimeout(r, 300));
      return { id: Math.random().toString(), name, color: "#6366f1" };
    },
    onSuccess: () => {
      setIsAddTagDialogOpen(false);
      setNewTagName("");
    },
  });

  const filteredBookmarks = bookmarks?.filter((bm) => {
    const matchesSearch =
      !searchQuery ||
      bm.article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      bm.article.summary?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTag = !selectedTag || bm.tags.some((t) => t.name === selectedTag);
    return matchesSearch && matchesTag;
  });

  return (
    <div className="flex h-full">
      {/* Sidebar - Tags */}
      <aside className="w-64 border-r bg-card/50 p-4 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold flex items-center gap-2">
            <Tag className="h-4 w-4" />
            标签
          </h2>
          <Dialog open={isAddTagDialogOpen} onOpenChange={setIsAddTagDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <Plus className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>创建新标签</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="tagName">标签名称</Label>
                  <Input
                    id="tagName"
                    placeholder="例如：机器学习"
                    value={newTagName}
                    onChange={(e) => setNewTagName(e.target.value)}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsAddTagDialogOpen(false)}>
                  取消
                </Button>
                <Button onClick={() => createTagMutation.mutate(newTagName)}>创建</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <ScrollArea className="flex-1">
          <div className="space-y-1">
            <Button
              variant={selectedTag === null ? "secondary" : "ghost"}
              className="w-full justify-start"
              onClick={() => setSelectedTag(null)}
            >
              <FolderOpen className="h-4 w-4 mr-2" />
              全部收藏
            </Button>
            {mockTags.map((tag) => (
              <Button
                key={tag.id}
                variant={selectedTag === tag.name ? "secondary" : "ghost"}
                className="w-full justify-start"
                onClick={() => setSelectedTag(tag.name)}
              >
                <div
                  className="h-3 w-3 rounded-full mr-2"
                  style={{ backgroundColor: tag.color }}
                />
                {tag.name}
              </Button>
            ))}
          </div>
        </ScrollArea>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50 sticky top-0 z-10">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <Bookmark className="h-6 w-6" />
                  我的收藏
                </h1>
                <p className="text-sm text-muted-foreground">
                  {filteredBookmarks?.length || 0} 篇收藏文章
                </p>
              </div>
              <div className="relative w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="搜索收藏..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
          </div>
        </header>

        <div className="flex-1 container mx-auto px-6 py-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : filteredBookmarks?.length === 0 ? (
            <Card className="py-12">
              <CardContent className="text-center">
                <Bookmark className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">暂无收藏</h3>
                <p className="text-sm text-muted-foreground">
                  在资讯列表中点击收藏按钮来添加收藏
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredBookmarks?.map((bookmark) => (
                <Card key={bookmark.id} className="group hover:shadow-md transition-shadow">
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-base line-clamp-2">
                          <a
                            href={bookmark.article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:text-primary transition-colors"
                          >
                            {bookmark.article.title}
                          </a>
                        </CardTitle>
                        <div className="flex items-center gap-2 mt-2">
                          {bookmark.tags.map((tag) => (
                            <Badge
                              key={tag.id}
                              variant="secondary"
                              className="text-xs"
                              style={{
                                backgroundColor: `${tag.color}20`,
                                color: tag.color,
                              }}
                            >
                              {tag.name}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-red-500 hover:text-red-600">
                          <Trash2
                            className="h-4 w-4"
                            onClick={() => deleteMutation.mutate(bookmark.id)}
                          />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
                          <a href={bookmark.article.url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {bookmark.article.summary && (
                      <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                        {bookmark.article.summary}
                      </p>
                    )}
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        收藏于 {new Date(bookmark.created_at).toLocaleDateString("zh-CN")}
                      </span>
                      {bookmark.article.author && <span>{bookmark.article.author}</span>}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
