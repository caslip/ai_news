"use client";

import { useState } from "react";
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
  Bell,
  BellOff,
} from "lucide-react";

interface MonitorItem {
  id: string;
  name: string;
  value: string;
  config: { keyword?: string; account?: string; username?: string; params?: Record<string, unknown> };
  is_active: boolean;
  monitor_type?: string;
  type?: string;
}

export default function MonitorPage() {
  const [isEnabled, setIsEnabled] = useState(true);
  const [newKeyword, setNewKeyword] = useState("");
  const [newAccount, setNewAccount] = useState("");
  const [isAddKeywordDialogOpen, setIsAddKeywordDialogOpen] = useState(false);
  const [isAddAccountDialogOpen, setIsAddAccountDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  // ─── 关键词 CRUD ──────────────────────────────────────────────

  const { data: keywords = [], isLoading: keywordsLoading } = useQuery<MonitorItem[]>({
    queryKey: ["monitor-keywords"],
    queryFn: async () => {
      const { apiClient } = await import("@/lib/api");
      const response = await apiClient.get("/api/monitor/keywords");
      return response.data || [];
    },
  });

  const addKeywordMutation = useMutation({
    mutationFn: async (name: string) => {
      const { apiClient } = await import("@/lib/api");
      const response = await apiClient.post("/api/monitor/keywords", {
        name,
        value: name,
        is_active: true,
      });
      return response.data;
    },
    onSuccess: () => {
      setIsAddKeywordDialogOpen(false);
      setNewKeyword("");
      queryClient.invalidateQueries({ queryKey: ["monitor-keywords"] });
    },
  });

  const deleteKeywordMutation = useMutation({
    mutationFn: async (id: string) => {
      const { apiClient } = await import("@/lib/api");
      await apiClient.delete(`/api/monitor/keywords/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["monitor-keywords"] });
    },
  });

  const toggleKeywordMutation = useMutation({
    mutationFn: async ({ id, is_active }: { id: string; is_active: boolean }) => {
      const { apiClient } = await import("@/lib/api");
      await apiClient.put(`/api/monitor/keywords/${id}`, { is_active });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["monitor-keywords"] });
    },
  });

  // ─── 账号 CRUD ──────────────────────────────────────────────

  const { data: accounts = [], isLoading: accountsLoading } = useQuery<MonitorItem[]>({
    queryKey: ["monitor-accounts"],
    queryFn: async () => {
      const { apiClient } = await import("@/lib/api");
      const response = await apiClient.get("/api/monitor/accounts");
      return response.data || [];
    },
  });

  const addAccountMutation = useMutation({
    mutationFn: async ({ name, value }: { name: string; value: string }) => {
      const { apiClient } = await import("@/lib/api");
      const response = await apiClient.post("/api/monitor/accounts", {
        name,
        value,
        is_active: true,
        monitor_type: "nitter",  // 默认创建为 Nitter 类型，统一由 X 监控管理
      });
      return response.data;
    },
    onSuccess: () => {
      setIsAddAccountDialogOpen(false);
      setNewAccount("");
      queryClient.invalidateQueries({ queryKey: ["monitor-accounts"] });
    },
  });

  const deleteAccountMutation = useMutation({
    mutationFn: async (id: string) => {
      const { apiClient } = await import("@/lib/api");
      await apiClient.delete(`/api/monitor/accounts/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["monitor-accounts"] });
    },
  });

  const toggleAccountMutation = useMutation({
    mutationFn: async ({ id, is_active }: { id: string; is_active: boolean }) => {
      const { apiClient } = await import("@/lib/api");
      await apiClient.put(`/api/monitor/accounts/${id}`, { is_active });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["monitor-accounts"] });
    },
  });

  const isLoading = keywordsLoading || accountsLoading;

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
                    <Radio className="h-4 w-4" />
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
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && newKeyword.trim()) {
                            addKeywordMutation.mutate(newKeyword.trim());
                          }
                        }}
                      />
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsAddKeywordDialogOpen(false)}>
                        取消
                      </Button>
                      <Button
                        onClick={() => addKeywordMutation.mutate(newKeyword.trim())}
                        disabled={!newKeyword.trim() || addKeywordMutation.isPending}
                      >
                        {addKeywordMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "添加"}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {isLoading ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                    </div>
                  ) : keywords.length > 0 ? (
                    keywords.map((kw) => (
                      <div key={kw.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50">
                        <span className={!kw.is_active ? "text-muted-foreground" : ""}>{kw.name}</span>
                        <div className="flex items-center gap-2">
                          <Switch
                            checked={kw.is_active}
                            onCheckedChange={(checked) =>
                              toggleKeywordMutation.mutate({ id: kw.id, is_active: checked })
                            }
                            id={`kw-${kw.id}`}
                          />
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 text-red-500 hover:text-red-600"
                            onClick={() => deleteKeywordMutation.mutate(kw.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center text-muted-foreground py-4">
                      暂无监控关键词
                    </div>
                  )}
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
                        placeholder="例如：karpathy"
                        value={newAccount}
                        onChange={(e) => setNewAccount(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && newAccount.trim()) {
                            addAccountMutation.mutate({
                              name: newAccount.trim(),
                              value: newAccount.trim(),
                            });
                          }
                        }}
                      />
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsAddAccountDialogOpen(false)}>
                        取消
                      </Button>
                      <Button
                        onClick={() =>
                          addAccountMutation.mutate({
                            name: newAccount.trim(),
                            value: newAccount.trim(),
                          })
                        }
                        disabled={!newAccount.trim() || addAccountMutation.isPending}
                      >
                        {addAccountMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "添加"}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {isLoading ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                    </div>
                  ) : accounts.length > 0 ? (
                    accounts.map((acc) => (
                      <div key={acc.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50">
                        <div className="flex items-center gap-2">
                          <span className={!acc.is_active ? "text-muted-foreground" : ""}>
                            @{acc.config.username || acc.config.account || acc.name}
                          </span>
                          {acc.monitor_type === "nitter" && (
                            <Badge variant="outline" className="text-xs bg-blue-500/10 text-blue-500 border-blue-500/30">
                              Nitter
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <Switch
                            checked={acc.is_active}
                            onCheckedChange={(checked) =>
                              toggleAccountMutation.mutate({ id: acc.id, is_active: checked })
                            }
                            id={`acc-${acc.id}`}
                          />
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 text-red-500 hover:text-red-600"
                            onClick={() => deleteAccountMutation.mutate(acc.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center text-muted-foreground py-4">
                      暂无监控账号
                    </div>
                  )}
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
                  <span className="text-sm text-muted-foreground">关键词数量</span>
                  <span className="font-semibold">{keywords.length}</span>
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">账号数量</span>
                  <span className="font-semibold">{accounts.length}</span>
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">活跃监控</span>
                  <span className="font-semibold text-green-600">
                    {keywords.filter((k) => k.is_active).length + accounts.filter((a) => a.is_active).length}
                  </span>
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

      </div>
    </div>
  );
}
