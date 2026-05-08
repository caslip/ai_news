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

export default function FavoritesPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [isAddTagDialogOpen, setIsAddTagDialogOpen] = useState(false);
  const [newTagName, setNewTagName] = useState("");
  const queryClient = useQueryClient();

  const { data: bookmarksData, isLoading } = useQuery({
    queryKey: ["favorites", selectedTag],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedTag) params.set("tag", selectedTag);
      params.set("page_size", "100");
      const res = await fetch(`/api/favorites?${params}`);
      if (!res.ok) throw new Error("Failed to fetch favorites");
      return res.json();
    },
  });

  const { data: tagsData } = useQuery({
    queryKey: ["favorite-tags"],
    queryFn: async () => {
      const res = await fetch("/api/favorites/tags");
      if (!res.ok) throw new Error("Failed to fetch tags");
      return res.json();
    },
  });

  const bookmarks = bookmarksData?.items || [];
  const tags = tagsData?.items || [];

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const res = await fetch(`/api/favorites/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete");
      return id;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["favorites"] }),
  });

  const createTagMutation = useMutation({
    mutationFn: async (name: string) => {
      const res = await fetch("/api/favorites/tags", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      if (!res.ok) throw new Error("Failed to create tag");
      return res.json();
    },
    onSuccess: () => {
      setIsAddTagDialogOpen(false);
      setNewTagName("");
      queryClient.invalidateQueries({ queryKey: ["favorite-tags"] });
    },
  });

  const filteredBookmarks = (bookmarks || []).filter((bm: Bookmark) => {
    const matchesSearch =
      !searchQuery ||
      bm.article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      bm.article.summary?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTag = !selectedTag || bm.tags.some((t: Tag) => t.name === selectedTag);
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
            {tags.map((tag: Tag) => (
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
              {filteredBookmarks?.map((bookmark: Bookmark) => (
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
                          {bookmark.tags.map((tag: Tag) => (
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
