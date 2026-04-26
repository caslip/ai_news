"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getSources,
  createSource,
  toggleSource,
  deleteSource,
  testSource,
  batchDeleteSources,
  Source,
  SourceCreate,
  SourceListResponse,
} from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Rss,
  RefreshCw,
  Plus,
  Trash2,
  Power,
  PowerOff,
  Play,
  Loader2,
  AlertCircle,
  CheckCircle,
  X,
} from "lucide-react";

const sourceTypeIcons: Record<string, any> = {
  rss: Rss,
  github: RefreshCw,
};

const sourceTypeColors: Record<string, string> = {
  rss: "text-orange-500 bg-orange-500/10",
  github: "text-purple-500 bg-purple-500/10",
};

export default function SourcesPage() {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [selectedSourceIds, setSelectedSourceIds] = useState<Set<string>>(new Set());
  const [newSource, setNewSource] = useState({
    name: "",
    type: "rss" as "rss" | "github",
    config: "",
    language: "",
  });

  const queryClient = useQueryClient();

  const { data, isLoading, refetch } = useQuery<SourceListResponse, Error>({
    queryKey: ["sources"],
    queryFn: () => getSources({ page_size: 100 }),
  });

  const toggleMutation = useMutation({
    mutationFn: (sourceId: string) => toggleSource(sourceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
  });

  const testMutation = useMutation({
    mutationFn: (sourceId: string) => testSource(sourceId),
  });

  const deleteMutation = useMutation({
    mutationFn: (sourceId: string) => deleteSource(sourceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
  });

  const batchDeleteMutation = useMutation({
    mutationFn: (sourceIds: string[]) => batchDeleteSources(sourceIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sources"] });
      setSelectedSourceIds(new Set());
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: SourceCreate) => createSource(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sources"] });
      setIsAddDialogOpen(false);
      setNewSource({
        name: "",
        type: "rss",
        config: "",
        language: "",
      });
    },
  });

  const handleAddSource = () => {
    let finalConfig: Record<string, any> = {};
    try {
      finalConfig = JSON.parse(newSource.config);
    } catch (e) {
      console.error("Invalid config JSON:", e);
      return;
    }

    createMutation.mutate({
      name: newSource.name,
      type: newSource.type,
      config: finalConfig,
    });
  };

  const getConfigDisplay = (type: string, config: Record<string, any>) => {
    if (type === "rss") return config.feed_url;
    if (type === "github") {
      const lang = config.language || "all";
      const since = config.since || "daily";
      return `Language: ${lang} | Since: ${since}`;
    }
    return "";
  };

  const toggleSelectAll = () => {
    if (!data) return;
    if (selectedSourceIds.size === data.items.length) {
      setSelectedSourceIds(new Set());
    } else {
      setSelectedSourceIds(new Set(data.items.map((s) => s.id)));
    }
  };

  const toggleSelectSource = (sourceId: string) => {
    const newSet = new Set(selectedSourceIds);
    if (newSet.has(sourceId)) {
      newSet.delete(sourceId);
    } else {
      newSet.add(sourceId);
    }
    setSelectedSourceIds(newSet);
  };

  const handleBatchDelete = () => {
    if (selectedSourceIds.size === 0) return;
    if (confirm(`确定要删除选中的 ${selectedSourceIds.size} 个信源吗？`)) {
      batchDeleteMutation.mutate(Array.from(selectedSourceIds));
    }
  };

  const isAllSelected = data && data.items.length > 0 && selectedSourceIds.size === data.items.length;

  return (
    <div className="flex flex-col h-full">
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Rss className="h-6 w-6" />
                信源管理
              </h1>
              <p className="text-sm text-muted-foreground">
                管理你的 RSS、Nitter、Twitter 和 GitHub 信息源
              </p>
            </div>
            {selectedSourceIds.size > 0 && (
              <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2">
                <span className="text-sm text-red-600 font-medium">
                  已选中 {selectedSourceIds.size} 个信源
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-red-600 hover:text-red-700 hover:bg-red-500/20"
                  onClick={handleBatchDelete}
                  disabled={batchDeleteMutation.isPending}
                >
                  {batchDeleteMutation.isPending ? (
                    <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4 mr-1" />
                  )}
                  批量删除
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 text-muted-foreground hover:text-foreground"
                  aria-label="清除选择"
                  onClick={() => setSelectedSourceIds(new Set())}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            )}
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4 mr-2" />
                刷新
              </Button>
              <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    添加信源
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>添加新信源</DialogTitle>
                    <DialogDescription>
                      配置你的 RSS 订阅源、Twitter 账号、Nitter 或 GitHub Trending
                    </DialogDescription>
                  </DialogHeader>

                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">名称</Label>
                      <Input
                        id="name"
                        placeholder="例如：机器之心"
                        value={newSource.name}
                        onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="type">类型</Label>
                      <Select value={newSource.type} onValueChange={(v) => setNewSource({ ...newSource, type: v as any })}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="rss">
                            <div className="flex items-center gap-2">
                              <Rss className="h-4 w-4 text-orange-500" />
                              RSS 订阅
                            </div>
                          </SelectItem>
                          <SelectItem value="github">
                            <div className="flex items-center gap-2">
                              <RefreshCw className="h-4 w-4 text-purple-500" />
                              GitHub Trending
                            </div>
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="config">配置</Label>
                      {newSource.type === "nitter" ? (
                        <Input
                          id="config"
                          placeholder="输入 Twitter 用户名，如 Khazix0918"
                          value={newSource.username}
                          onChange={(e) => setNewSource({ ...newSource, username: e.target.value })}
                        />
                      ) : (
                        <Textarea
                          id="config"
                          placeholder={
                            newSource.type === "rss"
                              ? '{"feed_url": "https://example.com/feed.xml"}'
                              : '{"language": "python", "since": "daily"}'
                          }
                          value={newSource.config}
                          onChange={(e) => setNewSource({ ...newSource, config: e.target.value })}
                          className="font-mono text-sm"
                        />
                      )}
                    </div>
                  </div>

                  <DialogFooter>
                    <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                      取消
                    </Button>
                    <Button onClick={handleAddSource}>添加</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 container mx-auto px-6 py-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[50px]">
                      <Checkbox
                        checked={isAllSelected}
                        onCheckedChange={toggleSelectAll}
                        aria-label="全选"
                      />
                    </TableHead>
                    <TableHead className="w-[250px]">名称</TableHead>
                    <TableHead>类型</TableHead>
                    <TableHead>配置</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>最后抓取</TableHead>
                    <TableHead className="text-right">操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data?.items.map((source) => {
                    const Icon = sourceTypeIcons[source.type] || Rss;
                    const colorClass = sourceTypeColors[source.type] || "";
                    const isSelected = selectedSourceIds.has(source.id);
                    return (
                      <TableRow
                        key={source.id}
                        className={`${!source.is_active ? "opacity-50" : ""} ${isSelected ? "bg-muted/50" : ""}`}
                      >
                        <TableCell>
                          <Checkbox
                            checked={isSelected}
                            onCheckedChange={() => toggleSelectSource(source.id)}
                            aria-label={`选择 ${source.name}`}
                          />
                        </TableCell>
                        <TableCell className="font-medium">{source.name}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className={colorClass}>
                            <Icon className="h-3 w-3 mr-1" />
                            {source.type.toUpperCase()}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground font-mono max-w-[200px] truncate">
                          {getConfigDisplay(source.type, source.config)}
                        </TableCell>
                        <TableCell>
                          {source.is_active ? (
                            <Badge variant="default" className="bg-green-500/10 text-green-600 hover:bg-green-500/10">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              启用
                            </Badge>
                          ) : (
                            <Badge variant="secondary">
                              <AlertCircle className="h-3 w-3 mr-1" />
                              禁用
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {source.last_fetched_at
                            ? new Date(source.last_fetched_at).toLocaleString("zh-CN")
                            : "从未"}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              onClick={() => testMutation.mutate(source.id)}
                              disabled={testMutation.isPending}
                            >
                              {testMutation.isPending ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Play className="h-4 w-4" />
                              )}
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              onClick={() => toggleMutation.mutate(source.id)}
                              disabled={toggleMutation.isPending}
                            >
                              {source.is_active ? (
                                <PowerOff className="h-4 w-4 text-orange-500" />
                              ) : (
                                <Power className="h-4 w-4 text-green-500" />
                              )}
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-red-500 hover:text-red-600"
                              onClick={() => {
                                if (confirm("确定要删除这个信源吗？")) {
                                  deleteMutation.mutate(source.id);
                                }
                              }}
                              disabled={deleteMutation.isPending}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
