"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Radio,
  Plus,
  Trash2,
  RefreshCw,
  Loader2,
  Clock,
  Search,
  Bell,
  BellOff,
} from "lucide-react";

interface MonitorKeyword {
  id: string;
  keyword: string;
  is_active: boolean;
}

interface MonitorAccount {
  id: string;
  account: string;
  is_active: boolean;
}

interface MonitorArticle {
  id: string;
  title: string;
  url: string;
  author: string;
  matched_keyword?: string;
  published_at: string;
  fetched_at: string;
}

const mockKeywords: MonitorKeyword[] = [
  { id: "1", keyword: "GPT-5", is_active: true },
  { id: "2", keyword: "Llama 4", is_active: true },
  { id: "3", keyword: "Claude 3.7", is_active: true },
  { id: "4", keyword: "AI Agent", is_active: false },
];

const mockAccounts: MonitorAccount[] = [
  { id: "1", account: "@karpathy", is_active: true },
  { id: "2", account: "@ylecun", is_active: true },
  { id: "3", account: "@sama", is_active: false },
];

const mockArticles: MonitorArticle[] = [
  {
    id: "1",
    title: "GPT-5 震撼发布！OpenAI 开启 AGI 新纪元",
    url: "https://twitter.com/example/status/1",
    author: "@sama",
    matched_keyword: "GPT-5",
    published_at: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    fetched_at: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
  },
  {
    id: "2",
    title: "Andrej Karpathy 教你从零实现 GPT-2",
    url: "https://twitter.com/karpathy/status/2",
    author: "@karpathy",
    published_at: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    fetched_at: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
  },
  {
    id: "3",
    title: "Meta 开源 Llama 4，性能超越 GPT-4",
    url: "https://twitter.com/ylecun/status/3",
    author: "@ylecun",
    matched_keyword: "Llama 4",
    published_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    fetched_at: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
  },
];

export default function MonitorPage() {
  const [isEnabled, setIsEnabled] = useState(true);
  const [newKeyword, setNewKeyword] = useState("");
  const [newAccount, setNewAccount] = useState("");
  const [isAddKeywordDialogOpen, setIsAddKeywordDialogOpen] = useState(false);
  const [isAddAccountDialogOpen, setIsAddAccountDialogOpen] = useState(false);
  const [sseConnected, setSseConnected] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    // 模拟 SSE 连接状态
    const timer = setTimeout(() => setSseConnected(true), 1000);
    return () => clearTimeout(timer);
  }, []);

  const { data: articles, isLoading } = useQuery({
    queryKey: ["monitor-articles"],
    queryFn: async () => {
      await new Promise((r) => setTimeout(r, 300));
      return mockArticles;
    },
  });

  const addKeywordMutation = useMutation({
    mutationFn: async (keyword: string) => {
      await new Promise((r) => setTimeout(r, 300));
      return { id: Math.random().toString(), keyword, is_active: true };
    },
    onSuccess: () => {
      setIsAddKeywordDialogOpen(false);
      setNewKeyword("");
      queryClient.invalidateQueries({ queryKey: ["monitor-keywords"] });
    },
  });

  const addAccountMutation = useMutation({
    mutationFn: async (account: string) => {
      await new Promise((r) => setTimeout(r, 300));
      return { id: Math.random().toString(), account, is_active: true };
    },
    onSuccess: () => {
      setIsAddAccountDialogOpen(false);
      setNewAccount("");
      queryClient.invalidateQueries({ queryKey: ["monitor-accounts"] });
    },
  });

  const toggleKeywordMutation = useMutation({
    mutationFn: async (id: string) => {
      await new Promise((r) => setTimeout(r, 200));
      return id;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["monitor-keywords"] }),
  });

  return (
    <div className="flex flex-col h-full">
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Radio className="h-6 w-6 text-sky-500" />
                X 监控
              </h1>
              <p className="text-sm text-muted-foreground">
                实时监控关键词和关注账号的推文
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Switch
                  checked={isEnabled}
                  onCheckedChange={setIsEnabled}
                  id="monitor-toggle"
                />
                <Label htmlFor="monitor-toggle" className="cursor-pointer">
                  {isEnabled ? (
                    <span className="flex items-center gap-1 text-green-600">
                      <Bell className="h-4 w-4" />
                      监控中
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-muted-foreground">
                      <BellOff className="h-4 w-4" />
                      已暂停
                    </span>
                  )}
                </Label>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={sseConnected ? "default" : "secondary"} className={sseConnected ? "bg-green-500" : ""}>
                  <span className={`h-2 w-2 rounded-full mr-1 ${sseConnected ? "bg-white animate-pulse" : "bg-gray-400"}`} />
                  {sseConnected ? "实时连接" : "连接中..."}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 container mx-auto px-6 py-6">
        <div className="grid grid-cols-3 gap-6">
          {/* Keywords */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Search className="h-4 w-4" />
                    关键词监控
                  </CardTitle>
                  <CardDescription>包含以下关键词的推文</CardDescription>
                </div>
                <Dialog open={isAddKeywordDialogOpen} onOpenChange={setIsAddKeywordDialogOpen}>
                  <DialogTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>添加监控关键词</DialogTitle>
                      <DialogDescription>
                        当推文包含这些关键词时会收到通知
                      </DialogDescription>
                    </DialogHeader>
                    <div className="py-4">
                      <Input
                        placeholder="例如：GPT-5, Claude..."
                        value={newKeyword}
                        onChange={(e) => setNewKeyword(e.target.value)}
                      />
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsAddKeywordDialogOpen(false)}>
                        取消
                      </Button>
                      <Button onClick={() => addKeywordMutation.mutate(newKeyword)}>
                        添加
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {mockKeywords.map((kw) => (
                    <div key={kw.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50">
                      <span className={!kw.is_active ? "text-muted-foreground" : ""}>{kw.keyword}</span>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={kw.is_active}
                          onCheckedChange={() => toggleKeywordMutation.mutate(kw.id)}
                          id={`kw-${kw.id}`}
                        />
                        <Button variant="ghost" size="icon" className="h-6 w-6 text-red-500 hover:text-red-600">
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Accounts */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Radio className="h-4 w-4" />
                    关注账号
                  </CardTitle>
                  <CardDescription>监控这些账号的推文</CardDescription>
                </div>
                <Dialog open={isAddAccountDialogOpen} onOpenChange={setIsAddAccountDialogOpen}>
                  <DialogTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>添加监控账号</DialogTitle>
                      <DialogDescription>
                        监控这些 Twitter/X 账号的推文
                      </DialogDescription>
                    </DialogHeader>
                    <div className="py-4">
                      <Input
                        placeholder="例如：@karpathy"
                        value={newAccount}
                        onChange={(e) => setNewAccount(e.target.value)}
                      />
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsAddAccountDialogOpen(false)}>
                        取消
                      </Button>
                      <Button onClick={() => addAccountMutation.mutate(newAccount)}>
                        添加
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {mockAccounts.map((acc) => (
                    <div key={acc.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50">
                      <span className={!acc.is_active ? "text-muted-foreground" : ""}>{acc.account}</span>
                      <div className="flex items-center gap-2">
                        <Switch checked={acc.is_active} id={`acc-${acc.id}`} />
                        <Button variant="ghost" size="icon" className="h-6 w-6 text-red-500 hover:text-red-600">
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">监控统计</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">今日抓取</span>
                  <span className="font-semibold">156</span>
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">触发通知</span>
                  <span className="font-semibold text-green-600">12</span>
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">平均延迟</span>
                  <span className="font-semibold">~2 分钟</span>
                </div>
                <Separator />
                <Button variant="outline" className="w-full" size="sm">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  手动刷新
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Live Feed */}
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Radio className="h-5 w-5 text-sky-500" />
            实时推送
            <Badge variant="secondary" className="ml-2">{articles?.length || 0} 条</Badge>
          </h2>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="space-y-3">
              {articles?.map((article) => (
                <Card key={article.id} className="group hover:shadow-md transition-shadow">
                  <CardContent className="pt-4">
                    <div className="flex items-start gap-3">
                      <div className="p-2 bg-sky-500/10 rounded-lg">
                        <Radio className="h-4 w-4 text-sky-500" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium">{article.author}</span>
                          {article.matched_keyword && (
                            <Badge variant="default" className="text-xs bg-sky-500">
                              #{article.matched_keyword}
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm line-clamp-2 mb-2">{article.title}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {new Date(article.published_at).toLocaleString("zh-CN")}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button variant="ghost" size="sm">
                          收藏
                        </Button>
                        <Button variant="ghost" size="sm" asChild>
                          <a href={article.url} target="_blank" rel="noopener noreferrer">
                            查看原文
                          </a>
                        </Button>
                      </div>
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
